import os
import json
import re
import zipfile
from datetime import datetime, timezone

# --- CONFIGURAÇÃO ---
# Pasta onde ficam os logs de mensagens (.jsonl), um arquivo por canal
LOG_DIR = "data/discord_export"
os.makedirs(LOG_DIR, exist_ok=True)

# --- HELPERS ---
def _sanitize_filename(name):
    """
    Remove/normaliza caracteres inválidos para nomes de arquivo no Windows/Linux.
    Retorna 'Sem-Categoria' se o nome vier vazio (canal sem categoria).
    """
    if not name:
        return "Sem-Categoria"

    # Caracteres proibidos em nomes de arquivo: \ / : * ? " < > |
    safe = re.sub(r'[\\/:*?"<>|]', '', name)
    safe = safe.strip().replace(' ', '-')

    return safe or "Sem-Categoria"

# --- LOGGING DE MENSAGENS ---
def log_message(message):
    """
    Registra uma mensagem em uma linha JSON (.jsonl) dentro de LOG_DIR,
    em um arquivo flat por canal (sem subpastas, pra zipar fácil).
    """
    category = message.channel.category.name if getattr(message.channel, 'category', None) else None
    channel_name = getattr(message.channel, 'name', str(message.channel.id))

    safe_category = _sanitize_filename(category)
    safe_channel = _sanitize_filename(channel_name)

    log_entry = {
        "id": message.id,
        "timestamp": message.created_at.isoformat(),
        "author": {
            "id": message.author.id,
            "name": message.author.name
        },
        "content": message.content,
        "attachments": [
            {"fileName": attachment.filename, "url": attachment.url}
            for attachment in message.attachments
        ]
    }

    file_name = f"{safe_category}__{safe_channel}_{message.channel.id}.jsonl"
    file_path = os.path.join(LOG_DIR, file_name)

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

# --- EXPORTAÇÃO (ZIP) ---
def build_export_zip():
    """
    Compacta todo o conteúdo de LOG_DIR em um .zip com timestamp (UTC) em data/.
    Retorna o caminho do arquivo .zip gerado.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join("data", f"discord_export_{timestamp}.zip")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name in os.listdir(LOG_DIR):
            full_path = os.path.join(LOG_DIR, file_name)
            if os.path.isfile(full_path):
                zipf.write(full_path, arcname=file_name)

    return zip_path
