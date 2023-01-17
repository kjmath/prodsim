# prodsim

Production simulator for multi-process manufacturing systems.

# Overview

This is a simulator for multi-process, manufacturing systems with production of discrete parts. It simulatates arrivals of raw materials, labor processes, part throughput, buffers, and queues. 

The simulation relies on 4 classes:

- The ```Process``` class characterizes a system process. It is defined by a name, statistical distribution characterizing process cycle time or process labor time, buffer capacity, maximum parts that can be serviced simultaneously, and a maximum number of workers per part for the process (if applicable). An instance of the ```Process``` class is created for each process in a factory.
- The ```PartType``` class characterizes different parts that are produced. It is defined by a name, a statistical distribution characterizing how stock arrives for the part’s production, and a list of ```Process``` objects characterizing the process that need to be performed to produce the part. ```Process``` objects can be shared between different ```PartType``` objects. An instance of the ```PartType``` class is created for each unique part type produced in the factory.
- The ```Worker``` class characterizes different workers in the factory. It is defined by a name and a set of ```Process``` class instances that the worker has the skills to work on. An instance of the ```Worker``` class is created for every worker in the factory. 
- The ```Factory``` class encapsulates all processes, parts, and workers in the factory. It is defined with a set of ```PartType``` objects containing the unique parts that will be produced in the factory, and a set of ```Worker``` objects characterizing every worker available in the factory. 

The main logic exists in the ```Factory``` class, which has an ```update_factory()``` method that moves the production in the factory forward. It calls helper methods that add arriving parts to the initial buffer, start and end processes, move parts into new processes, and allocate workers. 

# Usage

 This simulator uses yaml configuration files to specify production parameters. See **tests** folder for example yaml files. The yaml file is supplied as a command-line argument:

```python main.py path-to-yaml-config-file```

