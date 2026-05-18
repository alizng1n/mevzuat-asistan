"""
Zimbra E-Posta Entegrasyonu
İSTE Zimbra SOAP API ile iletişim kurarak gelen kutusu e-postalarını çeker ve sınıflandırır.
"""
import json
import os
import re
from datetime import datetime
from pythonzimbra.communication import Communication
from pythonzimbra.tools import auth

ZIMBRA_SOAP_URL = "https://eposta.iste.edu.tr/service/soap"

# Akademisyen e-posta listesini personnel.json'dan yükle
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _load_academic_emails():
    """Personnel veritabanından tüm akademisyen e-postalarını yükler."""
    emails = set()
    for fname in ["personnel_detailed.json", "personnel.json"]:
        path = os.path.join(PROJECT_ROOT, "data", fname)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for p in data:
                    email = p.get('email', '').strip().lower()
                    if email:
                        emails.add(email)
            except Exception:
                pass
            break
    return emails

# Duyuru kaynağı olarak bilinen e-posta kalıpları
ANNOUNCEMENT_PATTERNS = [
    "duyuru@", "bilgi@", "info@", "announcement@",
    "noreply@", "no-reply@", "sistem@", "system@",
    "haber@", "bulten@", "ogrenci@", "destek@",
    "ogrenciisleri@", "kayit@", "sinav@"
]

def classify_email(from_address: str, academic_emails: set) -> str:
    """
    E-postayı sınıflandırır.
    Returns: 'academic' | 'announcement' | 'other'
    """
    if not from_address:
        return 'other'
    
    addr = from_address.lower().strip()
    
    # Açılı parantez içinde gerçek e-posta adresini bul
    match = re.search(r'<(.+?)>', addr)
    if match:
        addr = match.group(1)
    
    # Duyuru kalıplarını kontrol et
    for pattern in ANNOUNCEMENT_PATTERNS:
        if pattern in addr:
            return 'announcement'
    
    # Akademisyen listesinde mi?
    if addr in academic_emails:
        return 'academic'
    
    # iste.edu.tr domaini ama listede değilse → muhtemelen idari/duyuru
    if addr.endswith('@iste.edu.tr'):
        return 'announcement'
    
    return 'other'


def zimbra_login(email: str, password: str) -> str:
    """
    Zimbra'ya giriş yapar ve auth token döndürür.
    Raises Exception on failure.
    """
    try:
        token = auth.authenticate(
            ZIMBRA_SOAP_URL,
            email,
            password,
            use_password=True
        )
        return token
    except Exception as e:
        raise Exception(f"Zimbra giriş başarısız: {str(e)}")


def fetch_inbox(token: str, limit: int = 50, offset: int = 0) -> list:
    """
    Zimbra gelen kutusundaki e-postaları çeker ve sınıflandırır.
    Returns list of email dicts.
    """
    academic_emails = _load_academic_emails()
    
    comm = Communication(ZIMBRA_SOAP_URL)
    search_request = comm.gen_request(token=token)
    search_request.add_request(
        'SearchRequest',
        {
            'query': 'in:inbox',
            'limit': str(limit),
            'offset': str(offset),
            'sortBy': 'dateDesc',
            'types': 'message'
        },
        'urn:zimbraMail'
    )
    
    response = comm.send_request(search_request)
    
    if response.is_fault():
        raise Exception(f"Zimbra arama hatası: {response.get_fault_message()}")
    
    result = response.get_response()
    
    # SearchResponse'dan mesajları çıkar
    search_resp = result.get('SearchResponse', {})
    messages_raw = search_resp.get('m', [])
    
    # Tek mesaj dict olarak dönebilir, listeye çevir
    if isinstance(messages_raw, dict):
        messages_raw = [messages_raw]
    
    emails = []
    for msg in messages_raw:
        # Gönderen bilgisini al
        from_addr = ''
        from_name = ''
        
        # e (email addresses) alanı
        e_list = msg.get('e', [])
        if isinstance(e_list, dict):
            e_list = [e_list]
        
        for e in e_list:
            if e.get('t') == 'f':  # 'f' = from
                from_addr = e.get('a', '')
                from_name = e.get('p', e.get('d', ''))
                break
        
        # Tarih (epoch ms → readable)
        date_ms = msg.get('d', 0)
        try:
            date_str = datetime.fromtimestamp(int(date_ms) / 1000).strftime('%d.%m.%Y %H:%M')
        except:
            date_str = ''
        
        # Konu
        subject = msg.get('su', '(Konu yok)')
        
        # Okundu mu?
        flags = msg.get('f', '')
        is_read = 'u' not in flags  # 'u' = unread
        
        # Sınıflandırma
        category = classify_email(from_addr, academic_emails)
        
        emails.append({
            'id': msg.get('id', ''),
            'subject': subject,
            'from_name': from_name,
            'from_address': from_addr,
            'date': date_str,
            'date_ms': date_ms,
            'is_read': is_read,
            'category': category,
            'snippet': msg.get('fr', '')[:150] if msg.get('fr') else ''
        })
    
    return emails
