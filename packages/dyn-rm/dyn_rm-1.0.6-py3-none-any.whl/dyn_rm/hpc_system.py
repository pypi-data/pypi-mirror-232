from abc import ABC, abstractmethod
from dyn_rm.my_pmix import *
from dyn_rm.util import *
import csv
import os

class System:

    def __init__(self, name, scheduling_policy, verbosity_level = 0):
        self.verbosity_level = verbosity_level
        self.name = name
        self.scheduling_policy = scheduling_policy
        self.procs = dict()
        self.node_pool = dict()
        self.jobs = dict()
        self.psets = dict()
        self.queue = []
        self.time = 0

    def __str__(self):
        return f"{self.jobid}"

    def apply_placeholder_setop(self, setop):

        num_procs = setop.get_proc_hard_request(setop.op)
        rank = num_procs
        job = self.jobs[setop.jobid]
        nodes_names = self.node_pool.keys()
        for node_name in nodes_names:
            if node_name not in setop.nodelist:
                continue
            node = self.node_pool[node_name]
            if len(node.proc_names) < node.num_slots: 
                num_slots_to_use = min(node.num_slots - len(node.proc_names), num_procs)
                num_procs -= num_slots_to_use
                self.job_add_node_names(job.name, [node_name])
                for i in range(num_slots_to_use):
                    self.add_procs([Proc("setop:"+str(setop.id), -rank, node_name)])
                    rank -= 1

            if num_procs == 0:
                break
        
    
    #####################################
    #Nodes
    #####################################
    def add_nodes(self, nodes):
        for node in nodes:
            self.node_pool[node.name] = node
    
    def remove_nodes(self, nodes):
        for node in nodes:
            self.node_pool.pop(node.name)
    
    def get_num_nodes(self):
        return len(self.node_pool.values())

    def node_set_slots(self, node_name, num_slots):
        self.node_pool[node_name].num_slots = num_slots
    
    # get all nodes that are not part of a job
    def get_free_nodes(self):
        free_nodes = [node.name for node in self.node_pool.values()]
        for job in self.jobs.values():
            for node in job.node_names:
                free_nodes.remove(node)
        return free_nodes

    
    #####################################
    #Jobs
    #####################################
    def add_jobs(self, jobs):
        for job in jobs:
            self.jobs[job.name] = job
    
    def remove_jobs(self, jobs):
        for job in jobs:
            self.jobs.pop(job.name)

    def job_add_node_names(self, jobid, node_names):
        if self.jobs.get(jobid) == None:
            self.add_jobs(Job(jobid))
        self.jobs[jobid].add_node_names(node_names)

    def job_remove_empty_nodes(self, jobid):
        job = self.jobs[jobid]
        node_names = job.node_names.copy()
        for node_name in node_names.keys():
            node = self.node_pool[node_name]
            empty = True
            for proc_name in node.proc_names.keys():
                if proc_name.split(':')[0] == jobid:
                    empty = False
            if empty:
                job.node_names.pop(node_name)

    #####################################
    #PSets
    #####################################
    def add_psets(self, psets):
        for pset in psets:
            self.psets[pset.name] = pset
            if pset.jobid != 'no_jobid':
                self.jobs[pset.jobid].pset_names[pset.name] = pset.name
    
    def pset_assign_to_job(self, pset_name, jobid):
        if self.psets.get(pset_name) == None:
            self.psets[pset_name] = PSet(pset_name, jobid)
        else:
            self.psets[pset_name].set_jobid(jobid)
        if self.jobs.get(jobid) == None:
            self.jobs[jobid] = Job(jobid)
        self.jobs[jobid].add_pset_names([pset_name])

    def pset_set_membership(self, pset_name, proc_names):
        if self.psets.get(pset_name) == None:
            self.psets.add(PSet("no_jobid", pset_name))
        self.psets[pset_name].set_membership(proc_names)
        self.psets[pset_name].size = len(proc_names)

    def remove_psets(self, psets):
        for pset in psets:
            self.psets.pop(pset.name)

    #####################################
    # Procs
    #####################################

    # add a proc to the proc_pool, job object and node
    def add_procs(self, procs):
        for proc in procs:
            self.procs[proc.name] = proc

            if not proc.jobid.startswith("setop:"):
                if self.jobs.get(proc.jobid) == None:
                    job = Job(proc.jobid)
                    self.add_jobs([job])
        
                self.jobs[proc.jobid].add_proc_names([proc.name])

            if self.node_pool.get(proc.node_name) == None:
                node = Node(proc.node_name, 8)
                self.add_nodes([node])
            self.node_pool[proc.node_name].add_procs([proc.name])

    def remove_procs(self, proc_names):
        for proc_name in proc_names:
            if not proc_name.startswith("setop:"):
                self.jobs[proc_name.split(':')[0]].proc_names.pop(proc_name)
            if proc_name in self.procs: 
                proc = self.procs[proc_name]
                self.node_pool[proc.node_name].remove_procs([proc_name])

    #####################################
    # SetOP
    #####################################
    def get_setop(self, setop_id):
        setop = None
        for job in self.jobs.values():
            for i in range(len(job.setops)):
                if job.setops[i].id == setop_id:
                    setop = job.setops[i]
        return setop

    def remove_setop(self, setop_id):
        for job_name in self.jobs.keys():
            for setop in self.jobs[job_name].setops:
                if setop.id == setop_id:
                    self.jobs[job_name].setops.remove(setop)
                    return
    
    def get_setops(self):
        setops=[]
        for job_name in self.jobs.keys():
            for setop in self.jobs[job_name].setops:
                setops.append(setop)
        return setops

    def setop_assign_to_job(self, jobid, setop):
        if self.jobs[jobid] == None:
            self.add_jobs[Job(jobid)]
        self.jobs[jobid].add_setop(setop)

    def setop_apply(self, setop_id, node_map = None, proc_map = None):
        setop = self.get_setop(setop_id)
        if None == setop:
            return

        job = self.jobs[setop.jobid]
        job.setops.remove(setop)


        # For SUB or SHRINK: just remove the processes & nodes from the job, delete the setop
        if setop.op == PMIX_PSETOP_SHRINK or setop.op == PMIX_PSETOP_SUB or setop.op == PMIX_PSETOP_REPLACE:
                pset_name = setop.output[0] # sub delta PSet is always the first ouput PSet
                pset = self.psets[pset_name]
                self.remove_procs([proc_name for proc_name in pset.procs.values()])
                self.job_remove_empty_nodes(job.name)
        # For ADD or GROW: remove placeholder processes, add new procs, delete setop
        if setop.op == PMIX_PSETOP_GROW or setop.op == PMIX_PSETOP_ADD or setop.op == PMIX_PSETOP_REPLACE:
            if None == node_map or None == proc_map:
                return
            num_procs = setop.get_proc_hard_request(setop.op)
            self.remove_procs([Proc.convert_to_procname("setop:"+str(setop.id), -(i+1)) for i in range(num_procs)])

            for node_name, procs in zip(node_map, proc_map):
                node = self.node_pool[node_name]
                if node not in job.node_names.keys():
                    job.node_names[node_name] = node_name
                for rank in procs.split(','):
                    proc_name = Proc.convert_to_procname(job.name, rank)
                    if proc_name not in node.proc_names.keys():
                        proc = Proc(job.name, rank, node_name) 
                        self.add_procs([proc])
                self.job_remove_empty_nodes(job.name)

    #####################################
    # Queue
    #####################################

    def get_waiting_job_size(waiting_job):
        argv = waiting_job[0].split(' ')
        for i in range(len(argv)):
            if argv[i] == '-np':
                return int(argv[i + 1])
        return 0
    
    # get the range of sizes a job can run on
    # returns dict with values for keys 'min', 'max', 'pref' (default = 0)
    def get_waiting_job_size_range(waiting_job):
        range = {'min' : 0, 'max' : 0, 'pref' : 0}

        argv = waiting_job[0].split(' ')
        for i in range(len(argv)):
            if argv[i] == '-np':
                sizes = argv[i + 1].split(',')
                if len(sizes > 0):
                    range['min'] = int(sizes[0])
                    if len(sizes) > 1:
                        range['max'] = int(sizes(1))
                        if len(sizes) > 2:
                            range['pref'] =int(sizes[2])
        return range
    
    def set_waiting_job_size(waiting_job, size):
        argv = waiting_job[0].split(' ')
        for i in range(len(argv)):
            if argv[i] == '-np':
                argv.insert(i, size)
        return 0    

    #####################################
    # Policy
    #####################################
    def set_policy(self, policy):
        self.scheduling_policy = policy            

    
    def schedule(self, parameter_list) -> dict:
        return self.scheduling_policy.schedule(self, parameter_list);

    #####################################
    # System Sate
    #####################################

    def get_num_free_slots(self):
        free_slots = 0

        for node in self.node_pool.values():
            if len(node.proc_names.values()) == 0:
                free_slots += node.num_slots

        return free_slots

    def print(self):
        
        print("")
        print("=================================================")
        print("CURRENT SYSTEM STATE OF SYSTEM '"+self.name+"':")
        print("=================================================")

        print("")
        print(" *********************")
        print("     NODES:")
        i = 1
        for node in self.node_pool.values():
            print("     "+str(i)+": "+node.name+"(slots="+str(node.num_slots)+")") 
            i = i+1
        print(" *********************")

        print("")
        print(" *********************")
        print("     JOBS:")
        i = 1
        for job in self.jobs.values():
            print("     "+str(i)+". '"+str(job.name)+"' (num_nodes = "+str(len(job.node_names))+", num_procs = "+str(len(job.proc_names))+" (+"
                    +str(sum([setop.get_proc_hard_request(PMIX_PSETOP_ADD) for setop in job.setops if setop.is_pending() and (setop.op == PMIX_PSETOP_ADD or setop.op == PMIX_PSETOP_GROW or setop.op == PMIX_PSETOP_REPLACE)]))+"/-"
                    +str(sum([setop.get_proc_hard_request(PMIX_PSETOP_SUB) for setop in job.setops if setop.is_pending() and (setop.op == PMIX_PSETOP_SUB or setop.op == PMIX_PSETOP_SHRINK or setop.op == PMIX_PSETOP_REPLACE)]))
                    +" pending), num_psets = "+str(len(job.pset_names))+")")
            print("         Nodes:")
            for node in job.node_names.values():
                print("             "+str(node)+"   ==>  Procs on this node : "+str([self.procs[proc].rank for proc in self.node_pool[node].proc_names.values()]))
            print("         PSets:")
            for pset in job.pset_names.values():
                print("             "+str(pset)+":  ==> Procs in this PSet: "+str([proc_name.split(':')[1] for proc_name in self.psets[pset].procs.values()]))
            print("         Number of Pending Set Operations:")
            print("             "+str(len([setop for setop in job.setops if setop.is_pending()])))
            i += 1
        print("===================================================")
        print()

    def write_output(self, filename, iter):
        if None == filename:
            return
        nodes = []
        for node in self.node_pool.keys():
            nodes.append(node)
        sorted(nodes)

        with open(filename, 'a+', newline='') as file:
            writer = csv.writer(file)
            if os.path.getsize(filename) == 0:
                header = ["Iteration"]
                for node in nodes:
                    header.append(node)
                writer.writerow(header)

            row = [iter]

            for node in nodes:
                occupied = False
                for job in self.jobs.values():
                    if node in job.node_names.keys():
                        row.append(job.name)
                        occupied = True;
                        break
                if not occupied:    
                    row.append("")

            writer.writerow(row)


    

class Job:

    def __init__(self, jobid):
        self.name = jobid
        self.node_names = dict()
        self.proc_names = dict()
        self.pset_names = dict()
        self.setops = []

    def __str__(self):
        return f"{self.name}"
    
    def add_node_names(self, node_names):
        for node_name in node_names:
            self.node_names[node_name] = node_name
    
    def remove_node_names(self, node_names):
        for node_name in node_names:
            self.node_names.pop(node_name)

    
    def add_proc_names(self, proc_names):
        for proc_name in proc_names:
            self.proc_names[proc_name] = proc_names
    
    def remove_proc_names(self, proc_names):
        for proc_name in proc_names:
            self.proc_names.pop(proc_name)

    def add_pset_names(self, pset_names):
        for pset_name in pset_names:
            self.pset_names[pset_name] = pset_name
    
    def remove_pset_names(self, pset_names):
        for pset_name in pset_names:
            self.pset_names.pop(pset_name)
    
    def add_setop(self, setop):
        self.setops.append(setop)

    def remove_setop(self, setop):
        self.setops.pop(setop)



class Node:
    def __init__(self, name, num_slots):
        self.name = name
        self.num_slots = num_slots
        self.proc_names = dict()


    def __str__(self):
        return f"{self.name}"
    
    def add_procs(self, procs):
        for proc in procs:
            self.proc_names[proc] = proc
    
    def remove_procs(self, procs):
        for proc in procs:
            self.proc_names.pop(proc)


class Proc:
    def __init__(self, jobid, rank, node_name):
        self.name = jobid+":"+str(rank)
        self.jobid = jobid
        self.rank = rank
        self.node_name = node_name
        


    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def convert_to_procname(jobid, rank):
        return str(jobid)+":"+str(rank)

class PSet:
    def __init__(self, jobid, name):
        self.jobid = jobid
        self.name = name
        self.size = 0
        self.procs = dict()
        
        
    def __str__(self):
        return f"{self.name}({self.size})"
    
    def set_membership(self, proc_names):
        for proc_name in proc_names:
            self.procs[proc_name] = proc_name
        size = len(self.procs)


    def set_jobid(self, jobid):
        self.jobid = jobid


class SetOp:
    def __init__(self, id, jobid, op, input, output, info, cbdata):
        self.id = id
        self.status = 0
        self.jobid = jobid
        self.op = op
        self.input = input
        self.output = output
        self.info = info
        self.cbdata = cbdata
        self.nodelist = []
        self.additional_info = []
        
    def __str__(self):
        return f"{self.op}: Input={[pset.name for pset in self.input]} Output={[pset.name for pset in self.output]}, Info={self.info}"

    def __eq__(self, other):
        if isinstance(other, SetOp):
            return self.id == other.id
        return False
    
    def is_unprocessed(self):
        return self.status == 0
    
    def is_pending(self):
        return self.status == 1

    def is_acknowleged(self):
        return self.status == 2
    
    def set_unprocessed(self):
        self.status = 0

    def set_processed(self):
        self.status = 1

    def set_acknowdlged(self):
        self.status = 2
    
    def from_info(event_infos):

        id = op = input = output = opinfo = jobid = None
        for event_info in event_infos:
            if event_info['key'] == "prte.alloc.reservation_number":
                id = event_info['value']
            elif event_info['key'] == "prte.alloc.client":
                jobid = event_info['value']['nspace'] 
            elif event_info['key'] == "mpi.rc_op_handle":
                for info in event_info['value']['array']:
                    if info['key'] == "pmix.psetop.type":
                        op = info['value']
                    if info['key'] == "mpi.op_info":
                        for mpi_op_info in info['value']['array']:
                            if mpi_op_info['key'] == "mpi.op_info.input":
                                input = mpi_op_info['value'].split(',')
                            elif mpi_op_info['key'] == "mpi.op_info.output":
                                output = mpi_op_info['value'].split(',')
                            elif mpi_op_info['key'] == "mpi.op_info.info":
                                op_info = mpi_op_info['value']['array']

        if op == None or id == None or input == None or output == None or jobid == None or op_info == None:
            return None

        return SetOp(id, jobid, op, input, output, op_info, event_info)
    

    def get_proc_hard_request(self, op):

        infos = self.additional_info if op == PMIX_PSETOP_REPLACE else self.info

        for info in infos:
            if op == PMIX_PSETOP_ADD or op == PMIX_PSETOP_GROW or op == PMIX_PSETOP_REPLACE:
                if info['key'] == "mpi_num_procs_add":               
                    return int(float(info['value']))
            elif op == PMIX_PSETOP_SUB or op == PMIX_PSETOP_SHRINK:
                if info['key'] == "mpi_num_procs_sub":               
                    return int(float(info['value']))
        

        return 0
    
    def get_proc_max(self):
        for info in self.info:
            if info['key'] == "mpi_num_procs_max":
                return int(info['value'])
        return -1

    def get_proc_min(self):
        for info in self.info:
            if info['key'] == "mpi_num_procs_min":
                return int(info['value'])
        return -1

    def get_proc_pref(self):
        for info in self.info:
            if info['key'] == "mpi_num_procs_pref":
                return int(info['value'])
        return -1


    def toString(self):
        return "Setop: op = "+str(self.op)+", job = "+str(self.jobid)+", input = "+str(self.input)+", output = "+str(self.output)+", info = "+str(self.info)+", nodelist = "+str(self.nodelist)+", additional_info = "+str(self.additional_info)

    

class SchedulingPolicy:

    def __init__(self, name, verbosity_level = 0):
        self.name = name
        self.verbosity_level = verbosity_level

    def schedule(self, my_system: System, params: list) -> dict:
        return self.scheduling_function(my_system, params)
    
    @abstractmethod
    def scheduling_function(self, my_system: System, params) -> dict:
        v_print("SCHEDULING RESOURCES OF SYSTEM '"+my_system.name+"' WITH POLICY '"+self.name+"'", 1, self.verbosity_level)


class Fifo_Hard_Requests(SchedulingPolicy):

    def scheduling_function(self, my_system: System, params: list) ->dict:
        super().scheduling_function(my_system, params)

        jobs_to_start = []
        setops_to_execute = []

        cur_free_slots = my_system.get_num_free_slots()
        cur_free_nodes = my_system.get_free_nodes()
        if len(my_system.queue) > 0:
            v_print("1. Checking if jobs from queue can be scheduled", 2, self.verbosity_level)
            for waiting_job in my_system.queue:
                
                job_size = System.get_waiting_job_size(waiting_job)
                if job_size <= cur_free_slots:
                    nodes = []
                    slots = 0
                    for node in my_system.node_pool.values():
                        if len(node.proc_names.values()) == 0:
                            nodes.append(node.name+":"+str(node.num_slots))
                            slots += node.num_slots
                            if slots >= job_size:
                                break
                    if slots >= job_size:
                        index_to_insert = waiting_job[0].index("-np")
                        my_system.queue.remove(waiting_job)
                        waiting_job[0] = waiting_job[0][:index_to_insert] + "--host "+','.join(nodes) +" "+ waiting_job[0][index_to_insert:]
                        return {"jobs_to_start" : [waiting_job], "setops_to_execute" : []}
        else: 
            v_print(" 1. There are no jobs in the job queue", 2, self.verbosity_level)

        v_print("  2. Checking for unprocessed Set Operations ...", 2, self.verbosity_level)
        for jobname in my_system.jobs.keys():
            job = my_system.jobs[jobname]
            if len(job.setops) > 0:
                for i in range(len(job.setops)):
                    setop = job.setops[i]
                    if(setop.is_unprocessed()):
                        v_print("     Checking if Setop '"+str(setop.id)+"' in job '"+job.name+"' can be executed", 3, self.verbosity_level)
                        if (setop.op == PMIX_PSETOP_SUB or  setop.op == PMIX_PSETOP_SHRINK):
                            if setop.get_proc_hard_request(PMIX_PSETOP_SUB) < len(job.proc_names) - sum([setop.get_proc_hard_request() for setop in job.setops if setop.is_pending() and (setop.op == PMIX_PSETOP_SUB or setop.op == PMIX_PSETOP_SHRINK)]):
                                v_print("         Setop '"+str(setop.id)+"' in job '"+job.name+"' is a substraction. Can be executed", 4, self.verbosity_level)
                                setop.set_processed()
                                setop.nodelist = [node for node in my_system.jobs[setop.jobid].node_names]
                                num_to_remove = setop.get_proc_hard_request(PMIX_PSETOP_SUB)
                                for node in list(reversed(list(job.node_names.values()))):
                                    if num_to_remove > 0:
                                        setop.nodelist.remove(node)
                                        num_to_remove -= my_system.node_pool[node].num_slots
                                    else:
                                        break
                                setops_to_execute.append(setop)
                            else:
                                v_print("         Setop '"+str(setop.id)+"' in job '"+job.name+"' is a substraction, but there are not enough procs in the job to substract "+str(setop.get_proc_hard_request())+" processes", 4, self.verbosity_level)
                                
                        elif  setop.op == PMIX_PSETOP_ADD or  setop.op == PMIX_PSETOP_GROW or setop.op == PMIX_PSETOP_REPLACE:
                            v_print("         Setop '"+str(setop.id)+"' in job '"+job.name+"' is an addition. Checking slots", 3, self.verbosity_level)
                            num_procs = setop.get_proc_hard_request(PMIX_PSETOP_ADD)
                            if num_procs > 0:
                                if cur_free_slots - num_procs >= 0:
                                    v_print("         Free slots = "+str(cur_free_slots)+" requested procs = "+str(num_procs)+" ==> GRANTED", 4, self.verbosity_level)
                                    setop.set_processed()
                                    setops_to_execute.append(setop)
                                    setop.nodelist = [node for node in my_system.jobs[setop.jobid].node_names]
                                    num_to_add = num_procs
                                    for node in cur_free_nodes:
                                        if num_to_add > 0:
                                            setop.nodelist.append(node)
                                            num_to_add -= my_system.node_pool[node].num_slots
                                        else:
                                            break
                                    
                                    my_system.apply_placeholder_setop(setop)
                                    cur_free_slots -= num_procs
                                else:
                                    v_print("         Free slots = "+str(cur_free_slots)+" requested procs = "+str(num_procs)+" ==> DENIED", 4, self.verbosity_level)
                        else:
                            #always execute setops which do not require resource changes
                            setops_to_execute.append(setop)
            else:
                v_print("         There are no setops in job "+job.name, 3, self.verbosity_level)

        return {"jobs_to_start" : jobs_to_start, "setops_to_execute" : setops_to_execute}

class DMR_Scheduler(SchedulingPolicy):

    def scheduling_function(self, my_system: System, params: list) ->dict:
        super().scheduling_function(my_system, params)

        jobs_to_start = []
        setops_to_execute = []
        #blocked_nodes = []

        cur_free_slots = my_system.get_num_free_slots()
        cur_free_nodes = my_system.get_free_nodes()
        if len(my_system.queue) > 0:
            v_print("1. Checking if jobs from queue can be scheduled", 2, self.verbosity_level)
            for waiting_job in my_system.queue:
                
                job_size = System.get_waiting_job_size(waiting_job)
                if job_size <= cur_free_slots:
                    nodes = []
                    slots = 0
                    for node in my_system.node_pool.values():
                        if len(node.proc_names.values()) == 0:
                            nodes.append(node.name+":"+str(node.num_slots))
                            #blocked_nodes.append(node.name)
                            slots += node.num_slots
                            if slots >= job_size:
                                break
                    if slots >= job_size:
                        index_to_insert = waiting_job[0].index("-np")
                        my_system.queue.remove(waiting_job)
                        waiting_job[0] = waiting_job[0][:index_to_insert] + "--host "+','.join(nodes) +" "+ waiting_job[0][index_to_insert:]
                        #cur_free_slots -= job_size
                        return {"jobs_to_start" : [waiting_job], "setops_to_execute" : []}
        else: 
            v_print(" 1. There are no jobs in the job queue", 2, self.verbosity_level)

        # Check if jobs can be resized to start a job from the job queue
        if len(my_system.queue) > 0:
           v_print("1. Checking if jobs from queue can be scheduled by resizing others", 2, self.verbosity_level)
           for waiting_job in my_system.queue:
               job_size = System.get_waiting_job_size(waiting_job)

               required_slots = job_size - cur_free_slots

               for jobname in my_system.jobs.keys():
                    job = my_system.jobs[jobname]
                    if len(job.setops) > 0:
                        rm_setops = []
                        for i in range(len(job.setops)):
                            setop = job.setops[i]
                            if(setop.is_unprocessed()):
                                v_print("     Checking if Setop '"+str(setop.id)+"' in job '"+job.name+"' can be executed", 3, self.verbosity_level)

                                if setop.op == PMIX_PSETOP_REPLACE:
                                    v_print("         Setop '"+str(setop.id)+"' in job '"+job.name+"' is an replace. Checking slots", 3, self.verbosity_level)
                
                                    pref = False
                                    if setop.get_proc_pref() != -1:
                                        pref = True
                                        min_procs = setop.get_proc_pref()
                                    else:
                                        min_procs = setop.get_proc_min()
                                    
                                    job_shrink = True
                                    
                                    if not pref:
                                        gathered_slots = 0
                                        aux_cur = cur_procs
                                        while gathered_slots < required_slots:
                                            aux_cur  = aux_cur / 2
                                            if aux_cur < min_procs:
                                                job_shrink = False
                                                break
                                            gathered_slots = cur_procs - aux_cur
                                        
                                        
                                        min_procs = cur_procs - gathered_slots 

                                        
                                    cur_procs = my_system.psets[setop.input[0]].size
                                    num_procs = cur_procs - min_procs

                                    if not job_shrink:
                                        continue

                                    if num_procs >= required_slots:
                                        
                                        v_print("         Free slots = "+str(cur_free_slots)+" requested procs = "+str(num_procs)+" ==> GRANTED", 4, self.verbosity_level)
                                        setop.set_processed()
                                        setop.additional_info.append({'key' : "mpi_num_procs_add", 'flags': 0, 'value' : str(0), 'val_type' : PMIX_STRING})
                                        setop.additional_info.append({'key' : "mpi_num_procs_sub", 'flags': 0, 'value' : str(num_procs), 'val_type' : PMIX_STRING})
                                        setops_to_execute.append(setop)
                                        setop.nodelist = [node for node in my_system.jobs[setop.jobid].node_names]
                                        #num_to_add = num_procs
                                        #occupied_nodes = []
                                        #for node in cur_free_nodes:
                                        #    if num_to_add > 0:
                                        #        setop.nodelist.append(node)
                                        #        occupied_nodes.append(node)
                                        #        num_to_add -= my_system.node_pool[node].num_slots
                                        #    else:
                                        #        break
#
                                        #for node in occupied_nodes:
                                        #    cur_free_nodes.remove(node)    
                                        #my_system.apply_placeholder_setop(setop)
                                        #cur_free_slots -= num_procs
                                        #else:

                                    #always execute setops which do not require resource changes
                                #    setops_to_execute.append(setop)
                                elif setop.op == PMIX_PSETOP_NULL:
                                    rm_setops.append(setop)
                                    setop.additional_info.append({'key' : "PMIX_PSETOP_CANCELED", 'flags': 0, 'value' : True, 'val_type' : PMIX_BOOL})
                                    setop.set_processed()
                                    setops_to_execute.append(setop)
                                elif setop.op == PMIX_PSETOP_CANCEL:
                                    setop.set_processed()
                                    setops_to_execute.append(setop)
                                    
                        for setop in rm_setops:
                            job.setops.remove(setop)
            


        if len(setops_to_execute) > 0:
            return {"jobs_to_start" : jobs_to_start, "setops_to_execute" : setops_to_execute}

        v_print("  2. Checking for unprocessed Set Operations ...", 2, self.verbosity_level)
        for jobname in my_system.jobs.keys():
            job = my_system.jobs[jobname]
            if len(job.setops) > 0:
                rm_setops = []
                for i in range(len(job.setops)):
                    setop = job.setops[i]
                    if(setop.is_unprocessed()):
                        v_print("     Checking if Setop '"+str(setop.id)+"' in job '"+job.name+"' can be executed", 3, self.verbosity_level)

                        if setop.op == PMIX_PSETOP_REPLACE:
                            v_print("         Setop '"+str(setop.id)+"' in job '"+job.name+"' is an addition. Checking slots", 3, self.verbosity_level)
                            max_procs = setop.get_proc_max()
                            cur_procs = my_system.psets[setop.input[0]].size

                            gathered_slots = 0
                            aux_cur = cur_procs
                            while aux_cur <= cur_free_slots:
                                aux_cur  = aux_cur * 2
                                if aux_cur > max_procs:
                                    aux_cur /= 2
                                    break
                            if aux_cur == cur_procs: # then check next
                                continue

                            max_procs = aux_cur


                            num_procs = max_procs - cur_procs
                            
                            if num_procs > 0:
                                if cur_free_slots - num_procs >= 0:
                                    v_print("         Free slots = "+str(cur_free_slots)+" requested procs = "+str(num_procs)+" ==> GRANTED", 4, self.verbosity_level)
                                    setop.set_processed()
                                    setop.additional_info.append({'key' : "mpi_num_procs_add", 'flags': 0, 'value' : str(num_procs), 'val_type' : PMIX_STRING})
                                    setop.additional_info.append({'key' : "mpi_num_procs_sub", 'flags': 0, 'value' : str(0), 'val_type' : PMIX_STRING})
                                    setops_to_execute.append(setop)
                                    setop.nodelist = [node for node in my_system.jobs[setop.jobid].node_names]
                                    num_to_add = num_procs
                                    occupied_nodes = []
                                    for node in cur_free_nodes:
                                        if num_to_add > 0:
                                            setop.nodelist.append(node)
                                            occupied_nodes.append(node)
                                            num_to_add -= my_system.node_pool[node].num_slots
                                        else:
                                            break
                                    
                                    my_system.apply_placeholder_setop(setop)
                                    for node in occupied_nodes:
                                        cur_free_nodes.remove(node)    
                                    cur_free_slots -= num_procs
                                else:
                                    v_print("         Free slots = "+str(cur_free_slots)+" requested procs = "+str(num_procs)+" ==> DENIED", 4, self.verbosity_level)
                        elif setop.op == PMIX_PSETOP_NULL:
                            rm_setops.append(setop)
                            setop.additional_info.append({'key' : "PMIX_PSETOP_CANCELED", 'flags': 0, 'value' : True, 'val_type' : PMIX_BOOL})
                            setop.set_processed()
                            setops_to_execute.append(setop)
                        elif setop.op == PMIX_PSETOP_CANCEL:
                            setop.set_processed()
                            setops_to_execute.append(setop)
                                    
                for setop in rm_setops:
                            job.setops.remove(setop)

                        #else:
                            #always execute setops which do not require resource changes
                        #    setops_to_execute.append(setop)
            else:
                v_print("         There are no setops in job "+job.name, 3, self.verbosity_level)

        return {"jobs_to_start" : jobs_to_start, "setops_to_execute" : setops_to_execute}
