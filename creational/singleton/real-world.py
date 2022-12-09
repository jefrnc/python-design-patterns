import random

class LoadBalancer:
    
    __instance = None
     
    
    def __init__(self):
        servers = [ "ServerI",
                    "ServerII",
                    "ServerIII",
                    "ServerIV",
                    "ServerV" ];
        
        self.servers = servers
        self.defaultServer = random.choice(self.servers)
        
    def __new__(cls, *args, **kwargs):
        print(cls.__instance)
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance
    
    def GetLoadBalancer(self):
        #return random item from self.servers        
        return random.choice(self.servers)

singleton = LoadBalancer()
singleton1 = LoadBalancer()
print("Get a load balancer instance")
print("Load Balancer - {}".format(singleton.GetLoadBalancer()))
print("Load Balancer - {}".format(singleton1.GetLoadBalancer()))
print("Load Balancer - {}".format(singleton.GetLoadBalancer()))
print("Load Balancer - {}".format(singleton1.GetLoadBalancer()))
print("-"*24)
print("Get the default server instance")
print("Retry #1 - {}".format(singleton.defaultServer))
print("Retry #2 - {}".format(singleton1.defaultServer))
print("Retry #3 - {}".format(singleton.defaultServer))
print("Retry #1 - {}".format(singleton1.defaultServer))