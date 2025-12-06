from simbricks.orchestration import system
from simbricks.orchestration import simulation as sim
from simbricks.orchestration.simulation.net import ns3_components
from simbricks.orchestration import instantiation as inst
from simbricks.orchestration.helpers import simulation as sim_helpers

"""
Fixed Ping ns-3 Example - Compatible with API 0.3.6
"""

instantiations = []

# ============ SYSTEM ============
sys = system.System()

# 创建主机和NIC
host0 = system.I40ELinuxHost(sys)
host0.add_disk(system.DistroDiskImage(sys, name="base"))  # 修复：使用 sys 而不是 h=host0
host0.add_disk(system.LinuxConfigDiskImage(sys, host0))

pcie0 = system.PCIeHostInterface(host0)
host0.add_if(pcie0)
nic0 = system.IntelI40eNIC(sys)
nic0.add_ipv4("10.0.0.1")
pcichannel0 = system.PCIeChannel(pcie0, nic0._pci_if)

host1 = system.I40ELinuxHost(sys)
host1.add_disk(system.DistroDiskImage(sys, name="base"))  # 修复：使用 sys 而不是 h=host1
host1.add_disk(system.LinuxConfigDiskImage(sys, host1))

pcie1 = system.PCIeHostInterface(host1)
host1.add_if(pcie1)
nic1 = system.IntelI40eNIC(sys)
nic1.add_ipv4("10.0.0.2")
pcichannel1 = system.PCIeChannel(pcie1, nic1._pci_if)

# 创建交换机
switch = system.EthSwitch(sys)
switch_nic0 = system.EthInterface(switch)
switch.add_if(switch_nic0)
switch_nic0_chan = system.EthChannel(nic0._eth_if, switch_nic0)
switch_nic0_chan.latency = 2 * 10**6

switch_nic1 = system.EthInterface(switch)
switch.add_if(switch_nic1)
switch_nic1_chan = system.EthChannel(nic1._eth_if, switch_nic1)
switch_nic1_chan.latency = 2 * 10**6

# 配置应用
sleep_app = system.Sleep(host0, infinite=True)
sleep_app.wait = False
host0.add_app(sleep_app)

ping_app = system.PingClient(host1, "10.0.0.1")
ping_app.wait = True
host1.add_app(ping_app)

# ============ SIMULATION ============
simulation = sim.Simulation("simple-ping-ns3-fixed", sys)

host_inst0 = sim.QemuSim(simulation)
host_inst0.add(host0)
host_inst0.name = "Server-Host"

nic_inst0 = sim.I40eNicSim(simulation)
nic_inst0.add(nic0)

host_inst1 = sim.QemuSim(simulation)
host_inst1.add(host1)
host_inst1.name = "Client-Host"

nic_inst1 = sim.I40eNicSim(simulation)
nic_inst1.add(nic1)

net_inst = sim.NS3Net(simulation)
net_inst.add(switch)
net_inst.global_conf.stop_time = '60s'

sim_helpers.disalbe_sync_simulation(simulation=simulation)

# ============ INSTANTIATION ============
instance = inst.Instantiation(sim=simulation)
instance.preserve_tmp_folder = False
instance.create_checkpoint = False

fragment = inst.Fragment()
fragment.add_simulators(*simulation.all_simulators())
instance.fragments = [fragment]

instantiations.append(instance)
