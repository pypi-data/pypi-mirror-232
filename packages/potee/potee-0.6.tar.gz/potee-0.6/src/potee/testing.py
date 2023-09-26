import random
from string import ascii_letters
import logging
import asyncio
import json
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('checker')

def generate_flag(n=24):
    return "".join(random.choices(ascii_letters, k=n))


class FlagStorage:
    storage: dict() = {}

    def add(self, name, flag, _id):
        self.storage[name] = {"flag": flag, "id": _id}

    def get(self, name):
        return self.storage[name].get("id")

    def validate(self, name, flag, _id):
        return tuple(self.storage[name].values()) == (flag, _id)


class ServiceTesting:
    iterations: int = 3
    actions: list = ["ping", "put", "get", "exploit"]
    host: str = "localhost"
    storage: FlagStorage = FlagStorage()
    hosts: list = []

    def save(self):
        with open("hosts.json", "w") as f:
            data = json.dumps(self.hosts)
            f.write(data)
    
    def run(self, functions):
        self.hosts = [{"id":1, "host": self.host}]
        self.save()
        for i in range(1, self.iterations):
            logger.info(f"iteration:{i}")
            for action in self.actions:
                #print(functions)
                for name, function in functions[action].items():
                    wrap, data = function
                    self.__getattribute__(action)(wrap, data, name)

    def ping(self, wrap, data, name):
        results = asyncio.run(wrap(*data)())
        for answer in results:
            if answer["answer"] == "pong":
                logger.info("ping => pong")
            else:
                logger.error(f"ping => {answer}")

    def put(self, wrap, data, name):
        flag = generate_flag()
        self.hosts[0]['flag'] = flag
        self.save()
        results = asyncio.run(wrap(*data)())
        
        for result in results:
            _id = result["answer"]
            self.storage.add(name, flag, _id)
            logger.info(f"put:{name}({flag}) => {_id}")

    def get(self, wrap, data, name):
        _id = self.storage.get(name)
        self.hosts[0]['value'] = _id
        self.save()
        results = asyncio.run(wrap(*data)())
        for result in results:
            flag = result["answer"]
            if self.storage.validate(name, flag, _id):
                logger.info(f"get:{name}({_id}) => {flag}")
            else:
                logger.error(f"get:{name}({_id}) => {flag}")

    def exploit(self, wrap, data, name):
        results = asyncio.run(wrap(*data)())
        for result in results:
            if result["answer"] == "yes":
                logger.info(f"exploit:{name} => exploitable") 
            elif result["answer"] == "no":
                logger.info(f"exploit:{name} => not exploitable") 
            else:
                logger.error(f"exploit:{name} => {result}") 
