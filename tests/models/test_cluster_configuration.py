import pytest

from aztk.models import ClusterConfiguration, Toolkit, UserConfiguration, SchedulingTarget
from aztk.spark.models.plugins import JupyterPlugin, HDFSPlugin
from aztk.error import InvalidModelError

def test_vm_count_deprecated():
    with pytest.warns(DeprecationWarning):
        config = ClusterConfiguration(vm_count=3)
        assert config.size == 3

    with pytest.warns(DeprecationWarning):
        config = ClusterConfiguration(vm_low_pri_count=10)
        assert config.size_low_priority == 10

    with pytest.warns(DeprecationWarning):
        config = ClusterConfiguration(size=10)
        assert config.vm_count == 10

    with pytest.warns(DeprecationWarning):
        config = ClusterConfiguration(size_low_priority=10)
        assert config.vm_low_pri_count == 10

    with pytest.warns(DeprecationWarning):
        config = ClusterConfiguration(size=10)
        config.vm_count = 20
        assert config.size == 20

    with pytest.warns(DeprecationWarning):
        config = ClusterConfiguration(size_low_priority=10)
        config.vm_low_pri_count = 20
        assert config.size_low_priority == 20

def test_size_none():
    config = ClusterConfiguration(size=None, size_low_priority=2)
    assert config.size == 0
    assert config.size_low_priority == 2


def test_size_low_priority_none():
    config = ClusterConfiguration(size=1, size_low_priority=None)
    assert config.size == 1
    assert config.size_low_priority == 0


def test_cluster_configuration():
    data = {
        'toolkit':  {
            'software': 'spark',
            'version': '2.3.0',
            'environment': 'anaconda'
        },
        'vm_size': 'standard_a2',
        'size': 2,
        'size_low_priority': 3,
        'subnet_id': '/subscriptions/21abd678-18c5-4660-9fdd-8c5ba6b6fe1f/resourceGroups/abc/providers/Microsoft.Network/virtualNetworks/prodtest5vnet/subnets/default',
        'plugins': [
            JupyterPlugin(),
            HDFSPlugin(),
        ],
        'user_configuration': {'username': 'spark'}
    }

    config = ClusterConfiguration.from_dict(data)

    assert isinstance(config.toolkit, Toolkit)
    assert config.toolkit.software == 'spark'
    assert config.toolkit.version == '2.3.0'
    assert config.toolkit.environment == 'anaconda'
    assert config.size == 2
    assert config.size_low_priority == 3
    assert config.vm_size == 'standard_a2'
    assert config.subnet_id == '/subscriptions/21abd678-18c5-4660-9fdd-8c5ba6b6fe1f/resourceGroups/abc/providers/Microsoft.Network/virtualNetworks/prodtest5vnet/subnets/default'

    assert isinstance(config.user_configuration, UserConfiguration)
    assert config.user_configuration.username == 'spark'

    assert len(config.plugins) == 2
    assert config.plugins[0].name == 'jupyter'
    assert config.plugins[1].name == 'hdfs'

def test_scheduling_target_dedicated_with_no_dedicated_nodes_raise_error():
    with pytest.raises(InvalidModelError, match="Scheduling target cannot be Dedicated if dedicated vm size is 0"):
        conf = ClusterConfiguration(
            cluster_id="abc",
            scheduling_target=SchedulingTarget.Dedicated,
            vm_size="standard_a2",
            size=0,
            size_low_priority=2,
            toolkit=Toolkit(software="spark", version="1.6.3"),
        )

        conf.validate()
