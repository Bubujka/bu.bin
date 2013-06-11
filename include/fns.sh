new_migration(){
        rake db:new_migration name="$1"
        vim-last db/migrations
}
