# tests/test_api.py
import requests
import json
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# URL da API (ajuste se necessário)
API_URL = "http://127.0.0.1:8000/api/v1"

def create_test_pdf(filename="test_document.pdf"):
    """Cria um PDF de teste simples para os testes da API."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Página 1: Introdução
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Capítulo 1: Introdução")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 120, "Este é o conteúdo da introdução.")
    c.showPage()

    # Página 2: Desenvolvimento
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Capítulo 2: Desenvolvimento")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 120, "Este é o conteúdo do desenvolvimento.")
    c.showPage()

    # Página 3: Conclusão
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Conclusão")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 120, "Este é o conteúdo da conclusão.")
    c.showPage()

    c.save()
    print(f"📄 PDF de teste '{filename}' criado com sucesso.")

def test_root_endpoint():
    """Testa o endpoint raiz da API."""
    print("\n🔍 Testando endpoint raiz...")
    try:
        response = requests.get("http://127.0.0.1:8000/")
        response.raise_for_status()  # Lança exceção para status de erro
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar à API: {e}")

def test_segment_pdf_endpoint():
    """Testa o endpoint de segmentação de PDF."""
    print("\n🔍 Testando segmentação de PDF...")
    pdf_file = "test_document.pdf"
    if not os.path.exists(pdf_file):
        print("PDF de teste não encontrado. Criando um novo...")
        create_test_pdf(pdf_file)

    try:
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file, f, 'application/pdf')}
            response = requests.post(f"{API_URL}/segment", files=files)
        
        response.raise_for_status()
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        print(f"Status do Processamento: {result.get('status')}")
        print(f"Mensagem: {result.get('message')}")
        
        chapters = result.get('chapters', [])
        print(f"Número de capítulos encontrados: {len(chapters)}")
        
        for i, chapter in enumerate(chapters, 1):
            print(f"\n📖 Capítulo {i}:")
            print(f"   Título: {chapter.get('title')}")
            print(f"   Página inicial: {chapter.get('start_page')}")
            content_preview = chapter.get('content', '')[:100].replace('\n', ' ')
            print(f"   Conteúdo (prévia): {content_preview}...")

    except requests.exceptions.HTTPError as e:
        print(f"❌ Erro HTTP: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")

def main():
    """Função principal para executar os testes."""
    print("🚀 Iniciando testes da API de Segmentação de PDFs")
    print("=" * 60)
    
    test_root_endpoint()
    test_segment_pdf_endpoint()
    
    # Limpa o arquivo de teste gerado
    if os.path.exists("test_document.pdf"):
        os.remove("test_document.pdf")
        print("\n🗑️ Arquivo de teste 'test_document.pdf' removido.")
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main()
