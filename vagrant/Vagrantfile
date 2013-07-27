Vagrant.configure("2") do |config|

# Box specific settings
    # Ubuntu 12.04 LTS Precise Pangolin
    config.vm.box = "precise32"
    config.vm.box_url = "http://files.vagrantup.com/precise32.box"
    
# Network specific settings
    config.vm.network :forwarded_port, guest: 8080, host:8080
    #config.vm.network :private_network, ip: "127.0.0.1"
    
# Provisioning
    config.vm.provision :shell, :path => "vagrantbootstrap.sh"
    
# Customization of virtual machine

  # config.vm.provider :virtualbox do |vb|
  #   # Don't boot with headless mode
  #   vb.gui = true
  #
  #   # Use VBoxManage to customize the VM. For example to change memory:
  #   vb.customize ["modifyvm", :id, "--memory", "1024"]
  # end    

    
#Sharing
    
    #Share the vagrant folder on the host OS with the home folder on guest OS
    #config.vm.synced_folder ".", "/Vagrant/"
    
end