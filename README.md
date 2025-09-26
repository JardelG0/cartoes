Criar chave SSH (Chave pública e Privada).
'''
ssh-keygen -t rsa -b 4096 -C "seu-email@exemplo.com"
'''

Local que é criado a chave pública.
'''
C:\Users\jarde\.ssh
'''

Exibir conteúdo da chave pública.
'''
cat ~/.ssh/id_rsa.pub
'''

Acessar o servidor com SSH
'''
ssh root@72.60.143.217
'''

Digie yes quando for solicitado
'''
Are you sure you want to continue conecting (yes/no/[fingerprint])? yes
'''

Para não informar o domínio e sair da configuração.
'''
CTRL + C
'''

Usar o Terminal conectado ao servidor para listar os arquivos.
'''
cd /usr/local/lsws/Example/html/demo
'''

Listar os arquivos do servidor
'''
ls -l
'''

Remover os arquivos do servidor
'''
rm -rf {*,.*}
'''

Clonar os arquivos do repositório do github.
'''
git clone git@github.com:JardelG0/cartoes.git .
'''

Verificar o python 3 instalado.
'''
python3 --version
'''

Atualizar a lista de pacotes
'''
sudo apt update
'''

Instalar o pacote para instalar o ambiente virtual
'''
sudo apt install python3-venv -y
'''

Criar o ambiente virtual
'''
python3 -m venv venv
'''

Ativar o ambiente virtual no linux
'''
source venv/bin/activate
'''

Instalar as dependências.
'''
pip install -r requirements.txt
'''

No GitHub, vá para settings (configurações) do seu repositório ou da sua conta, em seguida, vá para SSH and GPG keys e clique em New SSH key.
<br>
Cole a chave pública no campo fornecido e salve.<br>

Verificar a conexão com o GitHub.
'''
ssh -T git@github.com
'''

Verificar status do Firewall.
'''
sudo ufw status
'''

Permitir o acesso à porta 7080 para acessar o painel administrativo do OpenLiteSpeed.
'''
sufo ufw allow 7080
'''

Definir a senha do administrador do painel administrativo do OpenLiteSpeed.
'''
/usr/local/lsws/admin/misc/admpass.sh
'''

Acessar o painel Administrativo do OpenLiteSpeed
'''
http://72.60.143.217:7080
'''

Remover a permissão de acesso ao OpenLiteSpeed.
'''
sudo ufw delete allow 7080
'''

Alterar o "Owner" dos arquivos e diretórios de root para "nobody".
'''
sudo chown -R nobody:nogroup /usr/local/lsws/Example/html/demo
'''

Reiniciar o OpenLiteSpeed.
'''
/usr/local/lsws/bin/lswsctrl restart
'''

Limpar cache do PIP.
'''
pip cache purge
'''

Acessar a página inicial do site
'''
http://<ip-do-servidor>
'''
