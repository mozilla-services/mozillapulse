#
# Playdoh puppet magic for dev boxes
#
import "classes/*.pp"

# You can make these less generic if you like, but these are box-specific
# so it's not required.
$RABBITMQ_USER = 'pulse'
$RABBITMQ_PASSWORD = 'pulse'
$RABBITMQ_VHOST = 'pulse'
$RABBITMQ_HOST = 'localhost'
$RABBITMQ_PORT = '5672'

Exec {
    path => "/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin",
}

file {"/etc/profile.d/treeherder.sh":
    content => "
export PULSE_RABBITMQ_USER='${RABBITMQ_USER}'
export PULSE_RABBITMQ_PASSWORD='${RABBITMQ_PASSWORD}'
export PULSE_RABBITMQ_VHOST='${RABBITMQ_VHOST}'
export PULSE_RABBITMQ_HOST='${RABBITMQ_HOST}'
export PULSE_RABBITMQ_PORT='${RABBITMQ_PORT}'
"
}

class dev {
    class {
        init: before => Class[rabbitmq];
        rabbitmq:;
    }
}

include dev
