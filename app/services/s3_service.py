import boto3
import logging
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from app.core.config import settings
import io

logger = logging.getLogger(__name__)

class S3Service:
    """
    Serviço para gerir o upload de ficheiros para um bucket Amazon S3.
    """
    def __init__(self):
        """
        Inicializa o cliente S3 usando as credenciais das configurações.
        """
        try:
            if not all([settings.ACCESS_KEY_ID, settings.SECRET_ACCESS_KEY, settings.S3_BUCKET_NAME, settings.S3_ENDPOINT_URL]):
                raise ValueError("As credenciais e configurações da AWS não estão completas.")

            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.ACCESS_KEY_ID,
                aws_secret_access_key=settings.SECRET_ACCESS_KEY,
                # region_name=settings.REGION
            )
            self.bucket_name = settings.S3_BUCKET_NAME
            logger.info("Cliente S3 inicializado com sucesso.")
        except ValueError as e:
            logger.error(e)
            raise
        except (NoCredentialsError, PartialCredentialsError):
            logger.error("Credenciais da AWS não encontradas. Verifique o ficheiro .env ou as variáveis de ambiente.")
            raise ValueError("Credenciais da AWS não configuradas.")
        except Exception as e:
            logger.error(f"Erro inesperado ao inicializar o cliente S3: {e}")
            raise RuntimeError("Falha na inicialização do serviço S3.")

    def upload_audio(self, audio_bytes: bytes, filename: str) -> str:
        """
        Faz o upload de bytes de um ficheiro de áudio para o S3 e torna-o público.

        Args:
            audio_bytes: O conteúdo do áudio em bytes.
            filename: O nome do ficheiro (caminho) a ser guardado no bucket.

        Returns:
            A URL pública do ficheiro carregado.
        """
        try:
            file_obj = io.BytesIO(audio_bytes)
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                filename,
                ExtraArgs={'ContentType': 'audio/mpeg', 'ACL': 'public-read'}
            )
            
            # Constrói a URL pública do ficheiro
            url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{filename}"
            
            logger.info(f"Ficheiro '{filename}' carregado para o S3. URL: {url}")
            return url
        except ClientError as e:
            logger.error(f"Erro do cliente S3 ao fazer o upload: {e}")
            raise RuntimeError(f"Não foi possível carregar o ficheiro para o S3. Verifique as permissões do bucket.")
        except Exception as e:
            logger.error(f"Erro inesperado durante o upload para o S3: {e}")
            raise RuntimeError("Ocorreu uma falha desconhecida durante o upload do ficheiro.")

    def get_file(self, filename: str) -> bytes:
        """
        Obtém o conteúdo de um ficheiro do S3.

        Args:
            filename: O nome do ficheiro (caminho/chave) no bucket.

        Returns:
            O conteúdo do ficheiro em bytes.
        
        Raises:
            FileNotFoundError: Se o ficheiro não for encontrado no bucket.
            RuntimeError: Para outros erros de comunicação com o S3.
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=filename)
            file_content = response['Body'].read()
            logger.info(f"Ficheiro '{filename}' obtido com sucesso do S3.")
            return file_content
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.error(f"Ficheiro não encontrado no S3: {filename}")
                raise FileNotFoundError(f"O ficheiro '{filename}' não foi encontrado no bucket S3.")
            else:
                logger.error(f"Erro do cliente S3 ao obter o ficheiro '{filename}': {e}")
                raise RuntimeError(f"Não foi possível obter o ficheiro do S3.")
        except Exception as e:
            logger.error(f"Erro inesperado ao obter o ficheiro '{filename}' do S3: {e}")
            raise RuntimeError("Ocorreu uma falha desconhecida ao obter o ficheiro.")

