#!/usr/bin/env python

import binascii
import dataclasses
import datetime
import glob
import json
import logging
import os
import pathlib
import shutil
import socket
import subprocess
import time
import zipfile
from enum import Enum

from dacite import Config, from_dict
from kontor.defines import (
    ApplicantReadyMessage,
    AuthenticationFailureException,
    AuthRequestMessage,
    AuthResponseMessage,
    ClerkReadyMessage,
    ConnectionBrokenException,
    FileReceivingReceiptMessage,
    FileType,
    BureauOperationProtocol,
    ProcedureProtocol,
    InvalidMessageFormatException,
    ProcedureApprovalException,
    ProcedureExecutionException,
    ProcedureReceiptMessage,
    ProcedureRequestMessage,
    ProcedureResponseMessage,
    TransmissionType,
    UnexpectedMessageException,
    send_file,
    send_message,
    wait_and_receive_file,
    wait_and_receive_message,
)


class Clerk:
    def __init__(
        self,
        bureau_operation_protocol: BureauOperationProtocol,
        working_directory: str,
        temp_directory: str,
        applicant: socket.socket,
        address,
    ):
        self.__configuration = bureau_operation_protocol
        self.__working_directory = working_directory
        self.__temp_directory = temp_directory

        self.__applicant = applicant
        self.__address = address
        self.__is_bureau_shutting_down = False

    def __is_user_auth_correct(self, username: str, password_hash: str) -> bool:
        """
        Reading and parsing file every time function is called for loading file changes.
        Should be fine with small user databases.
        """
        user_db_filepath = os.path.join(self.__working_directory, "server_users.json")
        with open(user_db_filepath, "r", encoding="utf-8") as json_file:
            user_db_json = json.load(json_file)

        for user in user_db_json:
            if username == user["username"]:
                if password_hash == user["password_hash"]:
                    return True

        return False

    def __is_procedure_allowed_for_user(self, username: str, procedure: str) -> bool:
        """
        Reading and parsing file every time function is called for loading file changes.
        Should be fine with small user databases.
        """
        user_db_filepath = os.path.join(self.__working_directory, "server_users.json")
        with open(user_db_filepath, "r", encoding="utf-8") as json_file:
            user_db_json = json.load(json_file)

        for user in user_db_json:
            if username == user["username"]:
                if procedure in user["allowed_procedures"]:
                    return True

        return False

    def __is_file_accessible(self, address, file_path: str) -> bool:
        try:
            os.rename(file_path, file_path)

            if os.access(file_path, os.R_OK) and os.access(file_path, os.W_OK):
                return True

            return False

        except Exception as exception:
            logging.exception(
                "%s: Caught exception during file access checkup (%s).",
                address,
                str(exception),
            )
            return False

    def __wait_until_file_is_accessible(self, address, file_path: str):
        max_retries = 12
        for current_retry in range(max_retries):
            if self.__is_file_accessible(address, file_path):
                return

            logging.info(
                "%s: Waiting until file will be accessible for procedure (%d out of %d retries).",
                address,
                current_retry,
                max_retries,
            )
            time.sleep(5)

    def notify_about_shutdown(self):
        self.__is_bureau_shutting_down = True

    def provide_service(self):
        logging.info("%s: Starting new thread for connection.", self.__address)

        try:
            username = ""
            procedure = ""
            user_temp_folder_path = ""
            is_authenticated = False

            current_retry = 0
            max_connection_retries = 5
            try:
                for current_retry in range(max_connection_retries):
                    clerk_ready = ClerkReadyMessage(
                        applicant_ip=self.__address[0], applicant_port=self.__address[1]
                    )
                    send_message(
                        self.__applicant,
                        self.__address,
                        dataclasses.asdict(clerk_ready),
                    )

                    message_json = wait_and_receive_message(
                        self.__applicant, self.__address
                    )
                    _ = from_dict(
                        data_class=ApplicantReadyMessage,
                        data=message_json,
                        config=Config(cast=[Enum]),
                    )
                    break

            except socket.timeout:
                if current_retry == max_connection_retries - 1:
                    raise

                time.sleep(5)

            is_connection_alive = True
            while not self.__is_bureau_shutting_down and is_connection_alive:
                message_json = wait_and_receive_message(
                    self.__applicant, self.__address
                )

                if "type" not in message_json:
                    logging.error(
                        "%s: No 'type' stated in the incoming message, terminating connection.",
                        self.__address,
                    )
                    raise InvalidMessageFormatException(
                        f"{self.__address}: No 'type' stated in the incoming message, terminating connection."
                    )

                if message_json["type"] == TransmissionType.AUTH_REQUEST:
                    if is_authenticated:
                        auth_response = AuthResponseMessage(
                            is_authenticated=False, message="Unexpected message type."
                        )
                        send_message(
                            self.__applicant,
                            self.__address,
                            dataclasses.asdict(auth_response),
                        )
                        logging.error(
                            "%s: User is trying to re-authenticate while already being authenticated, terminating connection.",
                            self.__address,
                        )
                        raise UnexpectedMessageException(
                            f"{self.__address}: User is trying to re-authenticate while already being authenticated, terminating connection."
                        )

                    auth_request = AuthRequestMessage()
                    try:
                        auth_request = from_dict(
                            data_class=AuthRequestMessage,
                            data=message_json,
                            config=Config(cast=[Enum]),
                        )
                    except:
                        auth_response = AuthResponseMessage(
                            is_authenticated=False, message="Incorrect message format."
                        )
                        send_message(
                            self.__applicant,
                            self.__address,
                            dataclasses.asdict(auth_response),
                        )
                        logging.error(
                            "%s: No username or password stated in the incoming authentication request, terminating connection.",
                            self.__address,
                        )
                        raise

                    if not self.__is_user_auth_correct(
                        auth_request.username, auth_request.password_hash
                    ):
                        auth_response = AuthResponseMessage(
                            is_authenticated=False,
                            message="Incorrect username or password.",
                        )
                        send_message(
                            self.__applicant,
                            self.__address,
                            dataclasses.asdict(auth_response),
                        )
                        logging.error(
                            "%s: Username or password is incorrect, terminating connection.",
                            self.__address,
                        )
                        raise AuthenticationFailureException(
                            f"{self.__address}: Username or password is incorrect, terminating connection."
                        )

                    is_authenticated = True

                    auth_response = AuthResponseMessage(
                        is_authenticated=True, message="Authentication successful."
                    )
                    send_message(
                        self.__applicant,
                        self.__address,
                        dataclasses.asdict(auth_response),
                    )

                    timestamp = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
                    username = auth_request.username
                    user_temp_folder_path = os.path.join(
                        self.__temp_directory,
                        timestamp + "_" + username + f"_{self.__address[1]}",
                    )
                    pathlib.Path(user_temp_folder_path).mkdir(
                        parents=True, exist_ok=True
                    )
                    logging.debug(
                        "%s: Created temporary folder %s.",
                        self.__address,
                        user_temp_folder_path,
                    )

                if message_json["type"] == TransmissionType.PROCEDURE_REQUEST:
                    if not is_authenticated:
                        procedure_response = ProcedureResponseMessage(
                            is_ready_for_procedure=False,
                            message="User is not authenticated.",
                        )
                        send_message(
                            self.__applicant,
                            self.__address,
                            dataclasses.asdict(procedure_response),
                        )
                        logging.error(
                            "%s: User is not authenticated, terminating connection.",
                            self.__address,
                        )
                        raise UnexpectedMessageException(
                            f"{self.__address}: User is not authenticated, terminating connection."
                        )

                    procedure_request = ProcedureRequestMessage()
                    try:
                        procedure_request = from_dict(
                            data_class=ProcedureRequestMessage,
                            data=message_json,
                            config=Config(cast=[Enum]),
                        )
                    except:
                        procedure_response = ProcedureResponseMessage(
                            is_ready_for_procedure=False,
                            message="Incorrect message format.",
                        )
                        send_message(
                            self.__applicant,
                            self.__address,
                            dataclasses.asdict(procedure_response),
                        )
                        logging.error(
                            "%s: No file size, CRC32, name or procedure stated in the incoming authentication request, terminating connection.",
                            self.__address,
                        )
                        raise

                    if not self.__is_procedure_allowed_for_user(
                        username, procedure_request.procedure
                    ):
                        procedure_response = ProcedureResponseMessage(
                            is_ready_for_procedure=False,
                            message="User is not allowed to use selected procedure.",
                        )
                        send_message(
                            self.__applicant,
                            self.__address,
                            dataclasses.asdict(procedure_response),
                        )
                        logging.error(
                            "%s: User is not allowed to use selected procedure, terminating connection.",
                            self.__address,
                        )
                        raise ProcedureApprovalException(
                            f"{self.__address}: User is not allowed to use selected procedure, terminating connection."
                        )

                    procedure_response = ProcedureResponseMessage(
                        is_ready_for_procedure=True,
                        message="Procedure approved, ready to receive files.",
                    )
                    send_message(
                        self.__applicant,
                        self.__address,
                        dataclasses.asdict(procedure_response),
                    )

                    procedure = procedure_request.procedure

                    file_size_bytes = procedure_request.file_size_bytes
                    received_file_path = os.path.join(
                        user_temp_folder_path, procedure_request.file_name
                    )

                    wait_and_receive_file(
                        self.__applicant,
                        self.__address,
                        received_file_path,
                        procedure_request.file_size_bytes,
                    )

                    data_crc32: int = 0
                    with open(received_file_path, "rb") as processed_file:
                        data = processed_file.read()
                        data_crc32 = binascii.crc32(data) & 0xFFFFFFFF
                        data_crc32_str = "%08X" % data_crc32
                        logging.info(
                            "%s: Received file CRC32: %s.",
                            self.__address,
                            data_crc32_str,
                        )

                    if data_crc32_str != procedure_request.file_crc32:
                        procedure_receipt = FileReceivingReceiptMessage(
                            is_received_correctly=False,
                            message=f"File is received incorrectly, received CRC32 {data_crc32} differs to provided CRC32 {procedure_request.file_crc32}.",
                        )
                        send_message(
                            self.__applicant,
                            self.__address,
                            dataclasses.asdict(procedure_receipt),
                        )
                        logging.error(
                            "%s: File is received incorrectly, received CRC32 %s differs to provided CRC32 %s.",
                            self.__address,
                            data_crc32_str,
                            procedure_request.file_crc32,
                        )
                        raise ProcedureApprovalException(
                            f"{self.__address}: File is received incorrectly, received CRC32 {data_crc32} differs to provided CRC32 {procedure_request.file_crc32}."
                        )

                    file_size_bytes = os.path.getsize(received_file_path)
                    if file_size_bytes != procedure_request.file_size_bytes:
                        procedure_receipt = FileReceivingReceiptMessage(
                            is_received_correctly=False,
                            message=f"File is received incorrectly, received size {file_size_bytes} differs to provided size {procedure_request.file_size_bytes}.",
                        )
                        send_message(
                            self.__applicant,
                            self.__address,
                            dataclasses.asdict(procedure_receipt),
                        )
                        logging.error(
                            "%s: File is received incorrectly, received size %d differs to provided size %d.",
                            self.__address,
                            file_size_bytes,
                            procedure_request.file_size_bytes,
                        )
                        raise ProcedureApprovalException(
                            f"{self.__address}: File is received incorrectly, received size {file_size_bytes} differs to provided size {procedure_request.file_size_bytes}."
                        )

                    procedure_receipt = FileReceivingReceiptMessage(
                        is_received_correctly=True,
                        message="File is received correctly and being processed.",
                    )
                    send_message(
                        self.__applicant,
                        self.__address,
                        dataclasses.asdict(procedure_receipt),
                    )

                    file_paths = []
                    if procedure_request.file_type == FileType.SINGLE:
                        file_paths.append(received_file_path)
                    elif procedure_request.file_type == FileType.ARCHIVE:
                        with zipfile.ZipFile(received_file_path, "r") as zip_file:
                            zip_file.extractall(user_temp_folder_path)
                        os.remove(received_file_path)
                        file_paths = glob.glob(f"{user_temp_folder_path}/*")

                    for file_path in file_paths:
                        procedure_protocol = self.__configuration.procedures[procedure]
                        operation = procedure_protocol.operation

                        if "<FILE_NAME>" in operation:
                            operation = operation.replace("<FILE_NAME>", file_path)

                        if "<FILE_COPY>" in operation:
                            file_copy_path = file_path
                            extension = pathlib.Path(file_copy_path).suffix
                            file_copy_path = file_copy_path.replace(
                                extension, "_copy" + extension
                            )
                            operation = operation.replace("<FILE_COPY>", file_copy_path)
                            shutil.copy(file_path, file_copy_path)

                        is_procedure_failed = False
                        for retry_counter in range(
                            procedure_protocol.max_repeats_if_failed
                        ):
                            self.__wait_until_file_is_accessible(
                                self.__address, file_path
                            )

                            logging.info(
                                "%s: Executing procedure '%s' operation: '%s'. Retry %d of %d.",
                                procedure_protocol.name,
                                self.__address,
                                operation,
                                (retry_counter + 1),
                                procedure_protocol.max_repeats_if_failed,
                            )

                            result = subprocess.run(
                                operation,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                shell=True,
                                text=True,
                                universal_newlines=True,
                                check=False,
                            )

                            if result.returncode in procedure_protocol.error_codes:
                                if (
                                    retry_counter
                                    != procedure_protocol.max_repeats_if_failed - 1
                                ):
                                    time.sleep(
                                        procedure_protocol.time_seconds_between_repeats
                                    )
                                    continue
                                else:
                                    is_procedure_failed = True
                                    break

                            else:
                                break

                        if is_procedure_failed:
                            procedure_receipt = ProcedureReceiptMessage(
                                is_processed_correctly=False,
                                message=f"Procedure failed with return code {result.returncode} and error message {result.stdout}.",
                            )
                            send_message(
                                self.__applicant,
                                self.__address,
                                dataclasses.asdict(procedure_receipt),
                            )
                            logging.error(
                                "%s: Procedure failed with return code %d and error message %s.",
                                self.__address,
                                result.returncode,
                                result.stdout,
                            )
                            raise ProcedureExecutionException(
                                f"{self.__address}: Procedure failed with return code {result.returncode} and error message {result.stdout}."
                            )

                    if procedure_request.file_type == FileType.ARCHIVE:
                        with zipfile.ZipFile(received_file_path, "w") as zip_file:
                            for file in file_paths:
                                zip_file.write(
                                    file,
                                    os.path.basename(file),
                                    compress_type=zipfile.ZIP_DEFLATED,
                                )

                    processed_file_size_bytes = os.path.getsize(received_file_path)
                    processed_data_crc32: int = 0
                    with open(received_file_path, "rb") as processed_file:
                        processed_data = processed_file.read()
                        processed_data_crc32 = (
                            binascii.crc32(processed_data) & 0xFFFFFFFF
                        )
                        processed_data_crc32_str = "%08X" % processed_data_crc32
                        logging.info(
                            "%s: Processed file CRC32: %s.",
                            self.__address,
                            processed_data_crc32_str,
                        )

                    procedure_receipt = ProcedureReceiptMessage(
                        is_processed_correctly=True,
                        message="File was successfully processed.",
                        file_crc32=processed_data_crc32_str,
                        file_size_bytes=processed_file_size_bytes,
                    )
                    send_message(
                        self.__applicant,
                        self.__address,
                        dataclasses.asdict(procedure_receipt),
                    )

                    send_file(self.__applicant, self.__address, processed_data)

        except ConnectionBrokenException:
            logging.info("%s: Applicant disconnected.", self.__address)

        except Exception as exception:
            logging.exception("%s: %s.", self.__address, str(exception))

        finally:
            self.__applicant.shutdown(socket.SHUT_RDWR)
            self.__applicant.close()

            if self.__configuration.max_storage_period_hours == 0:
                shutil.rmtree(user_temp_folder_path)
                logging.debug(
                    "%s: Removed temporary folder %s.",
                    self.__address,
                    user_temp_folder_path,
                )
