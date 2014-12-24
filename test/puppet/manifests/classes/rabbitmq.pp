class rabbitmq {
    package { "rabbitmq-server":
        ensure => installed;
    }

    service { "rabbitmq-server":
        ensure => running,
        enable => true,
        require => Package['rabbitmq-server'];
    }

    exec{ "create-rabbitmq-user-test":
        command => "rabbitmqctl add_user pulse pulse",
        unless => "rabbitmqctl list_users | grep pulse",
        require => Service['rabbitmq-server']
    }

    exec{ "create-rabbitmq-user-code":
        command => "rabbitmqctl add_user code code",
        unless => "rabbitmqctl list_users | grep code",
        require => Service['rabbitmq-server']
    }

    exec{ "create-rabbitmq-user-build":
        command => "rabbitmqctl add_user build build",
        unless => "rabbitmqctl list_users | grep build",
        require => Service['rabbitmq-server']
    }

    exec{ "create-rabbitmq-vhost":
        command => "rabbitmqctl add_vhost ${RABBITMQ_VHOST}",
        unless => "rabbitmqctl list_vhosts | grep ${RABBITMQ_VHOST}",
        require => Service['rabbitmq-server']
    }

    exec{ "grant-rabbitmq-permissions-test":
        command => "rabbitmqctl set_permissions -p ${RABBITMQ_VHOST} pulse \"^(queue/pulse/.*|exchange/pulse/.*)\" \"^(queue/pulse/.*|exchange/pulse/.*)\" \"^(queue/pulse/.*|exchange/.*)\"",
        unless => "rabbitmqctl list_user_permissions pulse | grep -P \"${RABBITMQ_VHOST}\t^(queue/pulse/.*|exchange/pulse/.*)\t^(queue/pulse/.*|exchange/pulse/.*)\t^(queue/pulse/.*|exchange/.*)",
        require => [
            Exec["create-rabbitmq-user-test"],
            Exec["create-rabbitmq-vhost"]
        ]
    }

    exec{ "grant-rabbitmq-permissions-code":
        command => "rabbitmqctl set_permissions -p ${RABBITMQ_VHOST} code \"^(queue/code/.*|exchange/code/.*)\" \"^(queue/code/.*|exchange/code/.*)\" \"^(queue/code/.*|exchange/.*)\"",
        unless => "rabbitmqctl list_user_permissions code | grep -P \"${RABBITMQ_VHOST}\t^(queue/code/.*|exchange/code.*)\t^(queue/code/.*|exchange/code/.*)\t^(queue/code/.*|exchange/.*)",
        require => [
            Exec["create-rabbitmq-user-code"],
            Exec["create-rabbitmq-vhost"]
        ]
    }

    exec{ "grant-rabbitmq-permissions-build":
        command => "rabbitmqctl set_permissions -p ${RABBITMQ_VHOST} build \"^(queue/build/.*|exchange/build/.*)\" \"^(queue/build/.*|exchange/build/.*)\" \"^(queue/build/.*|exchange/.*)\"",
        unless => "rabbitmqctl list_user_permissions build | grep -P \"${RABBITMQ_VHOST}\t^(queue/build/.*|exchange/build/.*)\t^(queue/build/.*|exchange/build/.*)\t^(queue/build/.*|exchange/.*)",
        require => [
            Exec["create-rabbitmq-user-build"],
            Exec["create-rabbitmq-vhost"]
        ]
    }
}
