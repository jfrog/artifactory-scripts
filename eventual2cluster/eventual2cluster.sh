#!/bin/bash

echo "1. Please enter your requested function (1|2):"
select yn in "add" "delete"; do
    case $yn in
        add ) function=add; break;;
        delete ) function=delete; break;;
    esac
done
echo "setting function to $function"
if [[ ! $(pwd) = *"$function"* ]]; then
    echo "You are running the script in $(pwd), please be sure to run it in the _$function directory. Exiting..."
    exit
fi

read -p "2. Please enter your \$ARTIFACTORY_HOME installation user (default: artifactory):" artifactory_user
artifactory_user=${artifactory_user:-artifactory}
echo "Setting Artifactory user as $artifactory_user"
exists_flag=true
user_doesnt_exist=$(id -u $artifactory_user > /dev/null 2>&1; echo $?)
if [ "$user_doesnt_exist" = 1 ]; then
    echo "The user $artifactory_user does not appear to exist, do you want to continue? You may see some errors with permissions later on."
    select yin in "yes" "no"; do
        case $yin in
            yes ) exists_flag=false; echo "Continuing"; break;;
            no  ) echo "Exiting"; exit;;
        esac
    done
fi

read -p "3. Please enter your \$ARTIFACTORY_HOME installation group (default: artifactory):" artifactory_group
artifactory_group=${artifactory_group:-artifactory}
echo "Setting Artifactory group as $artifactory_group"
group_doesnt_exist=$(grep -i "^$artifactory_group" /etc/group)
if [ "$?" -eq 1 ]; then
    echo "The group $artifactory_group does not appear to exist, do you want to continue? You may see some errors with permissions later on."
    select yin in "yes" "no"; do
        case $yin in
            yes ) exists_flag=false; echo "Continuing"; break;;
            no  ) echo "Exiting"; exit;;
        esac
    done
fi

read -p "4. Please enter your eventual data directory (default: /var/opt/jfrog/artifactory/data/artifactory/eventual):" destination
destination=${destination:-/var/opt/jfrog/artifactory/data/eventual}
while [ ! -d "$destination" ]; do
      read -p "$destination doesn't exist, please enter your eventual data directory (\$ARTIFACTORY_HOME/data/eventual):" destination
done

echo "Setting queue directory to $destination/_queue"
if [ ! -d "$destination/_queue" ]; then
    echo "Creating _queue directory as it doesn't exist under $destination"
    mkdir -p $destination/_queue
fi

destination=$destination/_queue

echo "5. Would you like to copy or move the files?"
select yn in "copy" "move"; do
    case $yn in
        copy ) operation=cp; break;;
        move ) operation=mv; break;;
    esac
done
echo "setting operation to $operation"

for f in **/*
do

    filename=$(echo "$f" | cut -c 4-)
    curTime=$(date +%s%3N)
    echo "Running conversion for $filename"
    result=$filename-$curTime-$function
    echo "Result: $result"
    cpLoc=$destination/$result
    echo "Copying/Moving file to $cpLoc"
    $operation $f $cpLoc
done

if [ "$exists_flag" = true ]; then
    echo "Setting user permissions on the $destination/_queue directory to $artifactory_user:$artifactory_group. This may fail due to permissions of the user running the script..."
    chown -R $artifactory_user:$artifactory_group $destination
    echo "Finished setting permissions"
    else
        echo "Please be sure to run chown -R \$artifactory_user:\$artifactory_group $destination manually"
fi
echo "script complete."

