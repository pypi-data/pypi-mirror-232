class DataPack:
    def __init__(self):
        self.containers = []

    def add_container(self, *containervalues):
        self.containers.append(list(containervalues))

    def remove_container(self, containernumber):
        if containernumber < len(self.containers):
            del self.containers[containernumber]
        else:
            print("Container number does not exist.")

    def delete_container_value(self, containernumber, valuenumber):
        if containernumber < len(self.containers):
            container = self.containers[containernumber]
            if valuenumber < len(container):
                del container[valuenumber]
            else:
                print("Value number does not exist in the container.")
        else:
            print("Container number does not exist.")

    
