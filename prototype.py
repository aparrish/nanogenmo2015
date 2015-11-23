import random, sys
sentences = [line.split("\t")[1].strip() for line in sys.stdin]

while True:
    print " ".join(random.sample(sentences, random.randrange(1, 7)))
    print ""
