is_unix = RUBY_PLATFORM =~ /linux|darwin/ ? true : false
puts "host platform : #{RUBY_PLATFORM} (unix : #{is_unix})"

machines = {
    # name     => enabled
    :onlineweb => true
}

Vagrant.configure('2') do |config|

    if machines[:onlineweb]
        config.vm.define :onlineweb do |onlineweb_config|

            onlineweb_config.vm.box = 'precise32'
            onlineweb_config.vm.box_url = 'http://files.vagrantup.com/precise32.box'

            if is_unix
                puts 'unix forwarding (80 -> 8080, 8000 -> 8001, 443 -> 8443)'
                onlineweb_config.vm.network :forwarded_port, guest: 8000, host: 8001
                onlineweb_config.vm.network :forwarded_port, guest: 80, host: 8080
                onlineweb_config.vm.network :forwarded_port, guest: 443, host: 8443
            else
                puts 'windows forwarding (80 -> 80, 443 -> 443)'
                onlineweb_config.vm.network :forwarded_port, guest: 80, host: 80
                onlineweb_config.vm.network :forwarded_port, guest: 443, host: 443
            end

            onlineweb_config.ssh.forward_agent = true

            # nfs requires static IP
            #onlineweb_config.vm.synced_folder '.', '/vagrant/', :nfs => is_unix
            onlineweb_config.vm.synced_folder '.', '/vagrant/'

            onlineweb_config.vm.provider :virtualbox do |vbox|
                vbox.gui = false
                vbox.customize ['modifyvm', :id, '--natdnshostresolver1', 'on']
                #vbox.customize ['modifyvm', :id, '--memory', '256']
            end

            onlineweb_config.vm.provision :shell, :path => 'vagrantbootstrap.sh', :privileged => false
        end
    end
end
