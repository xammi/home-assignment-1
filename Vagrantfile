# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "ubuntu/precise32"

  config.vm.synced_folder "./", "/home/vagrant/home-assignment-1/"

  config.vm.provision "shell",
    path: "provision/run.sh"

  config.vm.provider :virtualbox do |vb|
    vb.gui = true
  end
end
