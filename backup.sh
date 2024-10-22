#!/bin/bash

# Настройки
DB_PATH="/app/data/preRecordingDatabase.db"
BACKUP_PATH="/app/data/PREdatabase_backup_$(date +\%Y-\%m-\%d).db"
SFTP_USER="Sasha"
SFTP_PASS="******"
SFTP_HOST="5.130.130.194"
SFTP_PORT="22"
SFTP_DEST_DIR="/tmp/mnt/7898866E98862B28/preRecordingBackup"

# Создание резервной копии базы данных
cp $DB_PATH $BACKUP_PATH

# Отправка резервной копии на SFTP сервер
sshpass -p $SFTP_PASS sftp -oPort=$SFTP_PORT -o StrictHostKeyChecking=no $SFTP_USER@$SFTP_HOST <<EOF
put $BACKUP_PATH $SFTP_DEST_DIR
bye
EOF

# Удаление локальной копии резервной копии
rm $BACKUP_PATH

echo "Бэкап успешно выполнен и передан на удаленный сервер."
