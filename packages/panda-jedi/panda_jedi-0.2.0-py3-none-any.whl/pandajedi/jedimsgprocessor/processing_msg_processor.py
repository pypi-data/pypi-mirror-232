import json

from pandajedi.jedimsgprocessor.base_msg_processor import BaseMsgProcPlugin

from pandacommon.pandalogger import logger_utils


# logger
base_logger = logger_utils.setup_logger(__name__.split(".")[-1])


# processing message processing plugin
class ProcessingMsgProcPlugin(BaseMsgProcPlugin):
    def process(self, msg_obj, decoded_data=None):
        # logger
        tmp_log = logger_utils.make_logger(base_logger, token=self.get_pid(), method_name="process")
        # start
        tmp_log.info("start")
        tmp_log.debug("sub_id={0} ; msg_id={1}".format(msg_obj.sub_id, msg_obj.msg_id))
        # parse
        if decoded_data is None:
            # json decode
            try:
                msg_dict = json.loads(msg_obj.data)
            except Exception as e:
                err_str = "failed to parse message json {2} , skipped. {0} : {1}".format(e.__class__.__name__, e, msg_obj.data)
                tmp_log.error(err_str)
                raise
        else:
            msg_dict = decoded_data
        # sanity check
        try:
            jeditaskid = int(msg_dict["workload_id"])
            # message type
            msg_type = msg_dict["msg_type"]
            if msg_type == "file_processing":
                target_list = msg_dict["files"]
            elif msg_type == "collection_processing":
                target_list = msg_dict["collections"]
            elif msg_type == "work_processing":
                pass
            else:
                raise ValueError("invalid msg_type value: {0}".format(msg_type))
            # relation type
            relation_type = msg_dict.get("relation_type")
        except Exception as e:
            err_str = "failed to parse message object dict {2} , skipped. {0} : {1}".format(e.__class__.__name__, e, msg_dict)
            tmp_log.error(err_str)
            raise
        # run
        try:
            # initialize to_proceed
            to_proceed = False
            # type filters
            if msg_type in ["file_processing", "collection_processing"] and relation_type in ["input"]:
                to_proceed = True
            # whether to proceed the targets
            if to_proceed:
                # initialize
                scope_name_dict_map = {}
                missing_files_dict = {}
                # loop over targets
                for target in target_list:
                    name = target["name"]
                    scope = target["scope"]
                    datasetid = target.get("external_coll_id", None)
                    fileid = target.get("external_content_id", None)
                    if (msg_type == "file_processing" and target["status"] in ["Available"]) or (
                        msg_type == "collection_processing" and target["status"] in ["Closed"]
                    ):
                        scope_name_dict_map.setdefault(scope, {})
                        scope_name_dict_map[scope][name] = (datasetid, fileid)
                    elif msg_type == "file_processing" and target["status"] in ["Missing"]:
                        # missing files
                        missing_files_dict[name] = (datasetid, fileid)
                    else:
                        # got target in bad attributes, do nothing
                        tmp_log.debug(
                            "jeditaskid={jeditaskid}, scope={scope}, msg_type={msg_type}, status={status}, did nothing for bad target".format(
                                jeditaskid=jeditaskid, scope=scope, msg_type=msg_type, status=target["status"]
                            )
                        )
                        pass
                # run by each scope
                for scope, name_dict in scope_name_dict_map.items():
                    # about files or datasets in good status
                    if msg_type == "file_processing":
                        tmp_log.debug("jeditaskid={0}, scope={1}, update about files...".format(jeditaskid, scope))
                        res = self.tbIF.updateInputFilesStagedAboutIdds_JEDI(jeditaskid, scope, name_dict)
                        if res is None:
                            # got error and rollback in dbproxy
                            err_str = "jeditaskid={0}, scope={1}, failed to update files".format(jeditaskid, scope)
                            raise RuntimeError(err_str)
                        tmp_log.info("jeditaskid={0}, scope={1}, updated {2} files".format(jeditaskid, scope, res))
                    elif msg_type == "collection_processing":
                        tmp_log.debug("jeditaskid={0}, scope={1}, update about datasets...".format(jeditaskid, scope))
                        res = self.tbIF.updateInputDatasetsStagedAboutIdds_JEDI(jeditaskid, scope, name_dict)
                        if res is None:
                            # got error and rollback in dbproxy
                            err_str = "jeditaskid={0}, scope={1}, failed to update datasets".format(jeditaskid, scope)
                            raise RuntimeError(err_str)
                        tmp_log.info("jeditaskid={0}, scope={1}, updated {2} datasets".format(jeditaskid, scope, res))
                    # send message to contents feeder if new files are staged
                    if res > 0 or msg_type == "collection_processing":
                        tmp_s, task_spec = self.tbIF.getTaskWithID_JEDI(jeditaskid)
                        if tmp_s and task_spec.is_msg_driven():
                            self.tbIF.push_task_trigger_message("jedi_contents_feeder", jeditaskid)
                            tmp_log.debug("pushed trigger message to jedi_contents_feeder for jeditaskid={0}".format(jeditaskid))
                    # check if all ok
                    if res == len(target_list):
                        tmp_log.debug("jeditaskid={0}, scope={1}, all OK".format(jeditaskid, scope))
                    elif res < len(target_list):
                        tmp_log.warning("jeditaskid={0}, scope={1}, only {2} out of {3} done...".format(jeditaskid, scope, res, len(target_list)))
                    elif res > len(target_list):
                        tmp_log.warning("jeditaskid={0}, scope={1}, strangely, {2} out of {3} done...".format(jeditaskid, scope, res, len(target_list)))
                    else:
                        tmp_log.warning("jeditaskid={0}, scope={1}, something unwanted happened...".format(jeditaskid, scope))
                # handle missing files
                n_missing = len(missing_files_dict)
                if n_missing > 0:
                    res = self.tbIF.setMissingFilesAboutIdds_JEDI(jeditaskid=jeditaskid, filenames_dict=missing_files_dict)
                    if res == n_missing:
                        tmp_log.debug("jeditaskid={0}, marked all {1} files missing".format(jeditaskid, n_missing))
                    elif res < n_missing:
                        tmp_log.warning("jeditaskid={0}, only {1} out of {2} files marked missing...".format(jeditaskid, res, n_missing))
                    elif res > n_missing:
                        tmp_log.warning("jeditaskid={0}, strangely, {1} out of {2} files marked missing...".format(jeditaskid, res, n_missing))
                    else:
                        tmp_log.warning("jeditaskid={0}, res={1}, something unwanted happened about missing files...".format(jeditaskid, res))
            else:
                # do nothing
                tmp_log.debug(
                    "jeditaskid={jeditaskid}, msg_type={msg_type}, relation_type={relation_type}, nothing done".format(
                        jeditaskid=jeditaskid, msg_type=msg_type, relation_type=relation_type
                    )
                )
        except Exception as e:
            err_str = "failed to process the message, skipped. {0} : {1}".format(e.__class__.__name__, e)
            tmp_log.error(err_str)
            raise
        # done
        tmp_log.info("done")
