require 'rbconfig'

def get_os
    @os ||= (
        host_os = RbConfig::CONFIG['host_os']
        case host_os
        when /mswin|msys|mingw|cygwin|bccwin|wince|emc/
            :"windows"
        when /darwin|mac os/
            :"macosx"
        when /linux/
            :"linux"
        when /solaris|bsd/
            :"unix"
        else
            raise Error::WebDriverError, "unknown os: #{host_os.inspect}"
        end
    )
end

os = get_os.to_s
  
puts "host platform : #{RUBY_PLATFORM} (operative system : #{os})"

machines = {
    # name     => enabled
    :onlineweb => true
}

Vagrant.configure('2') do |config|

    if machines[:onlineweb]
        config.vm.define :onlineweb do |onlineweb_config|

            onlineweb_config.vm.box = 'ubuntu/trusty32'
            # Commented out by hernil for now
            #onlineweb_config.vm.box_url = 'http://files.vagrantup.com/precise32.box'
            
            onlineweb_config.vm.network :forwarded_port, guest: 8000, host: 8001
            onlineweb_config.vm.network :forwarded_port, guest: 443, host: 8443

            onlineweb_config.ssh.forward_agent = true

            # nfs requires static IP
            #onlineweb_config.vm.synced_folder '.', '/vagrant/', :nfs => (os == "linux")
            onlineweb_config.vm.synced_folder '.', '/vagrant/'

            onlineweb_config.vm.provider :virtualbox do |vbox|
                vbox.gui = false
                #vbox.customize ['modifyvm', :id, '--natdnshostresolver1', 'on']
                #vbox.customize ['modifyvm', :id, '--memory', '256']
            end

            onlineweb_config.vm.provision :shell, :path => 'vagrantbootstrap.sh', :privileged => false
        end
    end
end
