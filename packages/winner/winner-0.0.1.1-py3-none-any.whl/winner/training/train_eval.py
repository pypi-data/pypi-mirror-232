

from winner.comm import *
from concurrent import futures
from enum import Enum, auto
from threading import Thread, Lock
from typing import Callable, Tuple

import grpc
import logging
import os
import sys

logger = logging.getLogger("winner")
# logger_stream_handler = logging.StreamHandler()
# logger_stream_handler.setFormatter(
#     logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# )
# logger.addHandler(logger_stream_handler)
# logger.setLevel(logging.DEBUG)

class TrainingState(Enum):
    '''
        TrainingState describes set of flags to denote the current status of the training
    '''
    TrainingDone = 0
    TrainingFailed = auto()
    TrainingInProgress = auto()
    TrainingAborted = auto()
    TrainingInfoError = auto()
    TrainingInEvaluation = auto()
    TrainingEvaluationDone = auto()
    TrainingEvaluationError = auto()
    TrainingUnknown = auto()


class TrainServicer(acharya_train_eval_pb2_grpc.TrainServicer):
    trainID: int = 0
    success: int = -1
    training_flag: bool = False
    trainer: Callable[[str], bool] = None
    evaluator: Callable[[acharya_train_eval_pb2.Datum], tuple] = None
    message: str = ""

    def __init__(self):
        self.training_flag_lock = Lock()
        pass

    def isTraining_compare_and_swap(self, old, new) -> bool:
        with self.training_flag_lock:
            if self.training_flag == old:
                self.training_flag = new
                return True
            else:
                return False

    def TrainNER(self, request: acharya_train_eval_pb2.NERTrain, context):
        logger.debug("In Training Call... TrainNER")

        out = acharya_train_eval_pb2.NEROutput()

        if request.Entities != None:
            logger.info("Found entities, saving to NEREntities.json")
            self.createNEREntities(request.Entities)

        if self.isTraining_compare_and_swap(False, True):
            self.trainID = request.TrainID
            self.success = TrainingState.TrainingInProgress.value
            self.trainThread = Thread(target=self.StartTraining, args=(request.TrainData,))
            self.trainThread.start()
        else:
            out.message = "Training already in progress, cannot start new training"
            logger.error(out.message)
            self.success = TrainingState.TrainingInProgress.value

        out.error = self.success
        return out

    def StartTraining(self, trainData):
        logger.info("Starting Training...")
        if self.trainer != None:
            self.message = "Training Started"
            self.trainer(trainData)
            self.success = TrainingState.TrainingDone.value
            self.message = "Training Done"
            self.isTraining_compare_and_swap(True, False)
        else:
            logger.error("No trainer set, cannot train. Set trainer func by calling SetTrainer")
            self.message = "No trainer set, cannot train. Set trainer func by calling SetTrainer"
            self.success = TrainingState.TrainingInfoError.value

    def SetTrainer(self, trainer: Callable[[str], bool]):
        self.trainer = trainer

    def SetEvaluationFn(self, evaluator: Callable[[str], bool]):
        self.evaluator = evaluator

    def createNEREntities(self, entities):
        with open("NEREntities.json", "w") as file:
            file.write(entities)

    def TrainingRunningStatus(self, request: acharya_train_eval_pb2.ProbeTrain, context):
        logger.debug("In Training Running Call... TrainingRunningStatus")
        out = acharya_train_eval_pb2.TrainingRunningOutput()
        if self.trainID == request.TrainID:
            if self.training_flag:
                out.status = TrainingState.TrainingInProgress.value
                out.message = "Training is running"
            else:
                out.status = self.success
                out.message = self.message
            out.status = self.success
            out.message = "Training is running"
        else:
            out.status = TrainingState.TrainingInfoError.value
            out.message = "Unknown train ID trn" + str(request.TrainID)
        return out

    def TrainingEvaluation(self, request: acharya_train_eval_pb2.Data_Collection, context):
        logger.debug("In Training Evaluation Call... TrainingEvaluation")
        out = acharya_train_eval_pb2.TrainingOutput()

        logger.debug("Checking if training is running + " + str(self.training_flag))
        if self.training_flag:
            out.status = TrainingState.TrainingInProgress.value
            out.message = "Training is running"
        else:
            logger.debug("Beginning Evaluation")
            out.status = TrainingState.TrainingInEvaluation.value
            self.message = "Evaluation Started"
            logger.debug("Checking if evaluator is set")
            if self.evaluator != None:
                logger.debug("Evaluator is set, evaluating data")
                for data in request.Dataset:
                    (eo, success) = self.evaluator(data)
                    logger.debug("Evaluated data, success: " + str(success))
                    if success == False:
                        out.status = TrainingState.TrainingEvaluationError.value
                        out.message = "Failed to evaluate data" + data.data
                        break
                    evalOut = acharya_train_eval_pb2.EvalOutput(json_classified=eo.json_classified, error=eo.error)
                    out.eo.append(evalOut)
                out.status = TrainingState.TrainingDone.value
        logger.debug("Returning from TrainingEvaluation")
        return out

    def TrainWordEmbeddings(self, request, context):
        pass

class EvalData():
    def __init__(self, data: str) -> None:
        self.data = data

class EvalOutput():
    error: int = -1

    def __init__(self, json_output: str) -> None:
        self.json_classified = json_output

    def setError(self, error: int) -> None:
        self.error = error

class EvalServicer(acharya_train_eval_pb2_grpc.EvalServicer):

    def SetEvaluationFn(self, evaluator: Callable[[str], bool]):
        self.evaluator = evaluator

    def GetEval(self, request: acharya_train_eval_pb2.Datum, context):
        if self.evaluator != None:
            logger.debug("Evaluator is set, evaluating data")
            (eo, success) = self.evaluator(request)
            logger.debug("Evaluated data, success: " + str(success))
            evalOut = acharya_train_eval_pb2.EvalOutput(json_classified=eo.json_classified, error=eo.error)
            return evalOut
        evalOut = acharya_train_eval_pb2.EvalOutput(json_classified="", error=-1)
        return evalOut



class Train:
    max_workers: int = 10
    set_trainer: bool = False
    set_evaluator: bool = False
    DefaultListenAddress: str = "localhost:7707"

    def __init__(self, 
                 trainer: Callable[[str], bool], 
                 evaluator: Callable[[EvalData], Tuple[EvalOutput, bool]],
                 listen_address: str = None
                ) -> None:
        if trainer != None:
            self.trainer = trainer
            self.set_trainer = True

        if evaluator != None:
            self.evaluator = evaluator
            self.set_evaluator = True

        self.address = self.validate_listen_address(listen_address)

    def validate_listen_address(self, address: str) -> str:
        if address == None:
            logger.warn("No listen address provided, using default.")
            logger.debug("The default address is" + self.DefaultListenAddress)
            return self.DefaultListenAddress

        if address == "":
            logger.error("Empty listen address provided, cannot start server.")
            return None

        if ((address.find(".sock") > 0) and (address.find("unix:") < 0)):
            logger.debug("Found .sock in address, assuming unix socket")
            socketPath = os.path.join(os.getcwd(), address)
            return "unix:///" + socketPath

        return address


    def Begin(self) -> bool:
        if self.set_trainer == False:
            logger.error("No trainer set, cannot train.")
            return False

        if self.set_evaluator == False:
            logger.error("No evaluator set, cannot evaluate.")
            return False

        t = TrainServicer()
        t.SetTrainer(self.trainer)
        t.SetEvaluationFn(self.evaluator)

        e = EvalServicer()
        e.SetEvaluationFn(self.evaluator)

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))

        acharya_train_eval_pb2_grpc.add_TrainServicer_to_server(t, server)

        acharya_train_eval_pb2_grpc.add_EvalServicer_to_server(e, server)

        server.add_insecure_port(self.address)

        sys.stdout.flush()
        print("starting winner grpc server on " + self.address + " with pid: " + str(os.getpid()))
        sys.stdout.flush()
        server.start()

        server.wait_for_termination()

        return True


        



        
