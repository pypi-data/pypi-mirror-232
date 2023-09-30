
import random

def iob_read_sentences(iobFile: str) -> list:
    '''
        Reads the iobFile and returns a list of sentences
        Each sentence is a list of lines
    '''
    with open(iobFile, "r") as f:
        lines = f.readlines()

    sentences = []
    sentence = []
    for line in lines:
        if line.startswith("--DOCSTART--"):
            continue
        if line == "\n":
            sentences.append(sentence)
            sentence = []
        else:
            sentence.append(line)

    return sentences

def iob_dev_test_split(iobFile: str, devPercent: float, testPercent: float) -> (list, list, list):
    '''
        Splits the iobFile into train, test and dev files based on the percentages given
        Returns a tuple of (trainLines, testLines, devLines)
    '''

    def validatePercent(percent: float):
        if percent < 0 or percent > 1:
            raise ValueError("Percent should be between 0 and 1")

    validatePercent(devPercent)
    validatePercent(testPercent)

    sentences = iob_read_sentences(iobFile)

    random.shuffle(sentences)

    devCount = int(len(sentences) * devPercent)
    testCount = int(len(sentences) * testPercent)

    devLines = sentences[:devCount]
    testLines = sentences[devCount:devCount + testCount]
    trainLines = sentences[devCount + testCount:]

    return (trainLines, testLines, devLines)

