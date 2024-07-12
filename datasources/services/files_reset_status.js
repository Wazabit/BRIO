db = connect( 'mongodb://localhost/brio' );
db.files.updateMany({'status': 'in_use'},{'$set':{'status':'used'}});
exit