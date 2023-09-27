#! /bin/sh
echo "Empty search"
ldapsearch -x -H ldap://localhost:8080

echo "Search with dn"
ldapsearch -x -b "dc=example,dc=org" -H ldap://localhost:8080

echo "Bind as Bob"
ldapsearch -x -D "cn=bob,ou=people,dc=example,dc=org" -W -H ldap://localhost:8080 -b "ou=people,dc=example,dc=org"