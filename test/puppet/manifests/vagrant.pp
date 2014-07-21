#
# Playdoh puppet magic for dev boxes
#
import "classes/*.pp"

# You can make these less generic if you like, but these are box-specific
# so it's not required.
$RABBITMQ_USER = 'pulse'
$RABBITMQ_PASSWORD = 'pulse'
$RABBITMQ_VHOST = '/'
$RABBITMQ_HOST = 'localhost'
$RABBITMQ_PORT = '5672'

Exec {
    path => "/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin",
}

class dev {
    class {
        init: before => Class[rabbitmq];
        rabbitmq:;
    }
}

include dev
