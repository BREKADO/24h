from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest, DeleteMessagesRequest
import asyncio
import time

# Defina suas credenciais de API
api_id = '20866570'
api_hash = 'a8465577ad96500e34bcb915e7afb9fe'
phone_number = '+5541999537467'  # Se necessário para login

# Defina os IDs dos canais/grupos de origem e destino
source_channel_id = -1002241597878  # ID do canal/grupo de onde pegar a mídia
destination_channel_ids = [-4505471987, -1002041497896, -1002067563323, -1002084607691, -1001666023042, -1001387756477, -1002112216705, -1002012526045]  # IDs dos canais/grupos para onde repassar

# Horários específicos para repassar a mídia (formato 24h:60:60, exemplo: '14:30:00', '18:45:30')
scheduled_times = ['22:18:00', '22:47:00', '23:06:00', '23:32:00', '23:57:00', '00:27:00', '00:48:00', '01:12:00', '01:49:00', '02:23:00','02:52:00', '03:16:00', '03:47:00', '04:14:00']

# Contador de mensagens enviadas para cada grupo
message_counter = {dest_id: 0 for dest_id in destination_channel_ids}
# Armazena as últimas mensagens enviadas para cada grupo
last_message_ids = {dest_id: [] for dest_id in destination_channel_ids}

# Inicialize o cliente do Telethon
client = TelegramClient('session_name', api_id, api_hash)

async def forward_media():
    async with client:
        # Pegue a última mídia do canal/grupo de origem
        history = await client(GetHistoryRequest(
            peer=source_channel_id,
            limit=1,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))

        if history.messages:
            message = history.messages[0]

            # Verifica se a mensagem contém mídia e se é um vídeo
            if message.media and message.media.document.mime_type.startswith('video/'):
                for dest_channel_id in destination_channel_ids:
                    # Envia o vídeo junto com o texto original
                    sent_message = await client.send_file(dest_channel_id, message.media, caption=message.message)
                    print(f"Vídeo repassado para {dest_channel_id} com texto.")

                    # Atualizar o contador e armazenar o ID da mensagem enviada
                    message_counter[dest_channel_id] += 1
                    last_message_ids[dest_channel_id].append(sent_message.id)

                    # Se tiver enviado 9 mensagens, apagar a mais antiga
                    if message_counter[dest_channel_id] > 9:
                        oldest_message_id = last_message_ids[dest_channel_id].pop(0)
                        await client(DeleteMessagesRequest(peer=dest_channel_id, id=[oldest_message_id]))
                        print(f"Mensagem antiga {oldest_message_id} apagada em {dest_channel_id}")

async def schedule_tasks():
    while True:
        now = time.strftime('%H:%M:%S')
        if now in scheduled_times:
            await forward_media()
            print(f"Mídia enviada no horário {now}")
            await asyncio.sleep(60)  # Espera 1 minuto para evitar múltiplos envios no mesmo minuto
        else:
            await asyncio.sleep(1)  # Verifica a cada segundo

if __name__ == '__main__':
    client.start(phone=phone_number)  # Se for a primeira vez, precisará do código de verificação

    loop = asyncio.get_event_loop()
    loop.run_until_complete(schedule_tasks())
