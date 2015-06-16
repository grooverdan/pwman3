# run this script with $ mongo < init_mongo.js

use pwmantest

db.createUser({user: "tester", pwd: "12345678",
              roles: [{role: "dbAdmin", db: "pwmantest"},
                      {role: "readWrite", db: "pwmantest"},]
              })

