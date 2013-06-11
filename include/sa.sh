sa(){
        ssh-agent | grep -v 'echo' > ~/.ssh_agent_info
        source .ssh_agent_info
        ssh-add ~/.ssh/id_rsa
}
