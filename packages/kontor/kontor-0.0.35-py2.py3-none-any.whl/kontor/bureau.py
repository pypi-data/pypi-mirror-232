#!/usr/bin/env python
import dataclasses
import hashlib
import json
import logging
import os
import pathlib
import socket
import threading
import time
from dataclasses import dataclass, field
from logging.handlers import TimedRotatingFileHandler

import pkg_resources

from kontor.clerk import Clerk
from kontor.defines import (
    BureauOperationProtocol,
    MissingWorkingDirectoryException,
    ProcedureAlreadyPresentException,
    ProcedureProtocol,
    ServerStartTimeoutException,
)


@dataclass
class ApplicantDossier:
    username: str = ""
    password_hash: str = ""
    allowed_procedures: list = field(default_factory=list)


class Bureau:
    def __init__(self, working_folder_path: str):
        self.__server: socket.socket
        self.__configuration: BureauOperationProtocol = BureauOperationProtocol()
        self.__is_server_started = False
        self.__is_bureau_shutting_down = False
        self.__server_threads = []
        self.__client_threads = []

        self.__working_directory = str(working_folder_path)
        pathlib.Path(self.__working_directory).mkdir(parents=True, exist_ok=True)

        self.__temp_directory = os.path.join(self.__working_directory, "temp")
        pathlib.Path(self.__temp_directory).mkdir(parents=True, exist_ok=True)

        #
        # Enable logging both to file and stdout.
        #
        log_directory = os.path.join(self.__working_directory, "logs")
        pathlib.Path(log_directory).mkdir(parents=True, exist_ok=True)

        filename = "bureau.log"
        filepath = os.path.join(log_directory, filename)

        handler = TimedRotatingFileHandler(filepath, when="midnight", backupCount=60)
        handler.suffix = "%Y%m%d"

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s:%(levelname)s %(message)s",
            handlers=[handler, logging.StreamHandler()],
        )

        try:
            kontor_version = pkg_resources.get_distribution("kontor").version
            logging.info("Initializing the bureau of version %s.", kontor_version)
        except pkg_resources.DistributionNotFound:
            logging.warning("bureau version was not found.")

        self.__parse_configuration_json_file()

    def __parse_configuration_json_file(self, configuration_filepath=None):
        """
        Try to locate configuration file in the working directory.
        """
        if configuration_filepath is None:
            configuration_filepath = os.path.join(
                self.__working_directory, "server_configuration.json"
            )

        #
        # Use default settings if no file was found. Create file with default settings.
        #
        if not os.path.exists(configuration_filepath):
            self.__save_configuration_to_json_file()
            return

        #
        # Read configuration JSON.
        #
        with open(configuration_filepath, "r", encoding="utf-8") as json_file:
            configuration_json = json.load(json_file)

        #
        # Parse configuration JSON.
        #
        if "ip_address" not in configuration_json:
            raise ValueError("No IP address was provided in configuration JSON!")

        self.__configuration.ip_address = configuration_json["ip_address"]

        if "port" not in configuration_json:
            raise ValueError("No port was provided in configuration JSON!")

        self.__configuration.port = configuration_json["port"]

        if "chunk_size_kilobytes" not in configuration_json:
            raise ValueError(
                "No transfer chunk size was provided in configuration JSON!"
            )

        self.__configuration.chunk_size_kilobytes = configuration_json[
            "chunk_size_kilobytes"
        ]

        if "client_idle_timeout_seconds" not in configuration_json:
            raise ValueError(
                "No client idle timeout was provided in configuration JSON!"
            )

        self.__configuration.client_idle_timeout_seconds = configuration_json[
            "client_idle_timeout_seconds"
        ]

        if "max_storage_period_hours" not in configuration_json:
            raise ValueError(
                "No max limit for storing temporary files was provided in configuration JSON!"
            )

        self.__configuration.max_storage_period_hours = configuration_json[
            "max_storage_period_hours"
        ]

        if "max_parallel_connections" not in configuration_json:
            raise ValueError(
                "No max limit for parallel connections was provided in configuration JSON!"
            )

        self.__configuration.max_parallel_connections = configuration_json[
            "max_parallel_connections"
        ]

        if "max_consequent_client_procedures" not in configuration_json:
            raise ValueError(
                "No max limit for consequent client procedures was provided in configuration JSON!"
            )

        self.__configuration.max_consequent_client_procedures = configuration_json[
            "max_consequent_client_procedures"
        ]

        if "max_grace_shutdown_timeout_seconds" not in configuration_json:
            raise ValueError(
                "No max grace shutdown timeout was provided in configuration JSON!"
            )

        self.__configuration.max_grace_shutdown_timeout_seconds = configuration_json[
            "max_grace_shutdown_timeout_seconds"
        ]

        self.__configuration.procedures = configuration_json["procedures"]

    def __save_configuration_to_json_file(self, configuration_filepath=None):
        if configuration_filepath is None:
            configuration_filepath = os.path.join(
                self.__working_directory, "server_configuration.json"
            )

        with open(configuration_filepath, "w", encoding="utf-8") as file:
            json.dump(
                dataclasses.asdict(self.__configuration),
                file,
                ensure_ascii=False,
                indent=4,
            )

    def __service_applicant_in_new_cubicle(self, clerk: Clerk, address):
        clerk.provide_service()

        #
        # Automatically remove itself from list of client threads.
        #
        self.__client_threads.remove(threading.current_thread())

        logging.info("%s: Thread for connection was closed.", address)

    def add_user(self, username: str, password: str, allowed_procedures: list):
        if not os.path.exists(self.__working_directory):
            raise MissingWorkingDirectoryException(
                "Working directory is not set, aborting start."
            )

        if not os.path.exists(self.__temp_directory):
            raise MissingWorkingDirectoryException(
                "Temporary directory is not set, aborting start."
            )

        new_user = ApplicantDossier()
        new_user.username = username
        new_user.password_hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
        new_user.allowed_procedures = allowed_procedures

        user_db_json = []
        user_db_filepath = os.path.join(self.__working_directory, "server_users.json")
        if os.path.exists(user_db_filepath):
            with open(user_db_filepath, "r", encoding="utf-8") as json_file:
                user_db_json = json.load(json_file)

        user_db_json.append(dataclasses.asdict(new_user))

        with open(user_db_filepath, "w", encoding="utf-8") as file:
            json.dump(
                user_db_json,
                file,
                ensure_ascii=False,
                indent=4,
            )

    def add_procedure(self, name: str, operation: str, overwrite: bool = False):
        if not os.path.exists(self.__working_directory):
            raise MissingWorkingDirectoryException(
                "Working directory is not set, aborting start."
            )

        if not os.path.exists(self.__temp_directory):
            raise MissingWorkingDirectoryException(
                "Temporary directory is not set, aborting start."
            )

        if not overwrite and name in self.__configuration.procedures:
            raise ProcedureAlreadyPresentException(
                f"Procedure {name} is already present in configuration."
            )

        procedure = ProcedureProtocol()
        procedure.name = name
        procedure.operation = operation
        procedure.error_codes = [1]

        self.__configuration.procedures[name] = procedure
        self.__save_configuration_to_json_file()

    def start_async(self):
        async_thread = threading.Thread(target=self.start, daemon=True)
        async_thread.start()
        self.__server_threads.append(async_thread)

        max_seconds_to_wait = 30
        timeout = time.time() + max_seconds_to_wait
        while not self.__is_server_started:
            time.sleep(1)

            if time.time() >= timeout:
                raise ServerStartTimeoutException(
                    f"Failed to start server in {max_seconds_to_wait} seconds!"
                )

    def start(self):
        if not os.path.exists(self.__working_directory):
            raise MissingWorkingDirectoryException(
                "Working directory is not set, aborting start."
            )

        if not os.path.exists(self.__temp_directory):
            raise MissingWorkingDirectoryException(
                "Temporary directory is not set, aborting start."
            )

        logging.info(
            "Opening bureau's reception at %s:%d.",
            self.__configuration.ip_address,
            self.__configuration.port,
        )

        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__server.bind((self.__configuration.ip_address, self.__configuration.port))
        self.__server.listen(self.__configuration.max_parallel_connections)
        self.__server.settimeout(0.5)

        logging.info("Starting to listen for incoming connections.")

        self.__is_server_started = True
        while not self.__is_bureau_shutting_down:
            try:
                client, address = self.__server.accept()

                logging.info("New incoming connection from %s.", address)

                client.settimeout(self.__configuration.client_idle_timeout_seconds)
                clerk = Clerk(
                    self.__configuration,
                    self.__working_directory,
                    self.__temp_directory,
                    client,
                    address,
                )

                thread = threading.Thread(
                    target=self.__service_applicant_in_new_cubicle,
                    args=(
                        clerk,
                        address,
                    ),
                )
                thread.start()
                self.__client_threads.append(thread)

            except socket.timeout:
                #
                # Ignore socket.timeout exception.
                #
                time.sleep(0.5)

            except Exception as exception:
                logging.info(
                    "Caught exception during waiting for new connections. Exception %s.",
                    str(exception),
                )
                time.sleep(0.5)

    def shutdown(self):
        """
        Gracefully shuts down the bureau, waiting for clerks to complete their job.
        Max wait is defined by bureau protocol.
        """
        logging.info("Shutting down the bureau.")

        self.__is_bureau_shutting_down = True

        # for _, clerk in self.__client_threads.items():
        #     clerk.notify_about_shutdown()

        grace_shutdown_start_time = time.process_time()
        while (
            len(self.__client_threads) > 0
            and (time.process_time() - grace_shutdown_start_time)
            >= self.__configuration.max_grace_shutdown_timeout_seconds
        ):
            logging.info(
                "Waiting for %d thread to complete their jobs (max wait %d seconds).",
                len(self.__client_threads),
                self.__configuration.max_grace_shutdown_timeout_seconds,
            )
            time.sleep(5)

        #
        # Somewhat weird way of stopping endlessly waiting socket.accept.
        #
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(
            (self.__configuration.ip_address, self.__configuration.port)
        )
        self.__server.close()

        if len(self.__server_threads) > 0:
            logging.info(
                "Server is running in async mode, waiting for thread to finish."
            )
            for async_thread in self.__server_threads:
                async_thread.join()

        logging.info("Shutdown complete.")
