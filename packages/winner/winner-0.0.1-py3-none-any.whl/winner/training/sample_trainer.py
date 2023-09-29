
import json
import logging

import winner.training as training

logger = logging.getLogger("winner")

logger_stream_handler = logging.StreamHandler()
logger_stream_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(logger_stream_handler)
logger.setLevel(logging.DEBUG)

def main():

    logger.info("In main")

    def train(trainData: str):
        logger.info("In train, received trainData: " + trainData)
        return True
    
    def evaluate(evalData: training.EvalData) -> (training.EvalOutput, bool):
        logger.info("In evaluate, received evalData: " + evalData)
        return (training.EvalOutput(json.dumps(evalData)), True)

    trainer = training.Train(train, evaluate, "testComm.sock")
    success = trainer.Begin()

    logger.info("Training finished with status: ", success)

if __name__ == "main":
    main()
