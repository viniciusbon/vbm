#!/usr/bin/env python3
# Instalar dependências (se necessário)
!pip install moviepy gtts pillow
!sudo apt-get install fonts-dejavu
from moviepy.editor import *
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageFilter
import os

# ============== CONFIGURAÇÕES ==============
# Caminhos (ajuste conforme seu Google Drive)
pasta_video = "/content/drive/MyDrive/video"
video_base = os.path.join(pasta_video, "01.mp4")
musica_background = os.path.join(pasta_video, "musica.mp3")
caminho_final = "/content/short_pronto.mp4"

# Frases a serem exibidas no vídeo
frases = [
    "Primeira frase emocionante para o seu short.",
    "Segunda frase com impacto.",
    "Terceira frase que prende a atenção.",
    "Quarta frase para manter o interesse.",
    "Última frase chamando para ação."
]

# ============== FUNÇÃO PARA TEXTO TRANSPARENTE COM TAMANHO DINÂMICO ==============
from PIL import Image, ImageDraw, ImageFont, ImageColor

from PIL import Image, ImageDraw, ImageFont, ImageColor
import os

def gerar_texto_imagem(texto, tamanho_video, proporcao_altura_max=0.45, proporcao_largura_max=0.9, cor='white', cor_borda='black', cor_sombra='gray'):
    """
    Cria imagem com texto centralizado, com sombra e contorno, ajustando a fonte automaticamente
    para caber no vídeo.
    """
    largura_video, altura_video = tamanho_video

    # Caminho para fonte TrueType
    caminho_fonte = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if not os.path.exists(caminho_fonte):
        raise FileNotFoundError("Fonte não encontrada: DejaVuSans-Bold.ttf")

    # Iniciar com a altura máxima permitida
    fontsize = int(altura_video * proporcao_altura_max)

    # Tentar reduzir a fonte até o texto caber dentro da largura máxima
    while fontsize > 10:
        fonte = ImageFont.truetype(caminho_fonte, fontsize)
        img_temp = Image.new("RGBA", tamanho_video, (0, 0, 0, 0))
        draw_temp = ImageDraw.Draw(img_temp)
        bbox = draw_temp.textbbox((0, 0), texto, font=fonte)
        texto_largura = bbox[2] - bbox[0]

        if texto_largura <= largura_video * proporcao_largura_max:
            break
        fontsize -= 1

    # Criar imagem final
    fonte = ImageFont.truetype(caminho_fonte, fontsize)
    img = Image.new("RGBA", tamanho_video, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bbox = draw.textbbox((0, 0), texto, font=fonte)
    texto_largura = bbox[2] - bbox[0]
    texto_altura = bbox[3] - bbox[1]
    x = (largura_video - texto_largura) // 2
    y = (altura_video - texto_altura) // 2

    # Sombra
    sombra_offset = 3
    draw.text((x + sombra_offset, y + sombra_offset), texto, font=fonte, fill=ImageColor.getrgb(cor_sombra) + (180,))

    # Contorno
    borda_offset = 2
    for dx in [-borda_offset, 0, borda_offset]:
        for dy in [-borda_offset, 0, borda_offset]:
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), texto, font=fonte, fill=ImageColor.getrgb(cor_borda) + (255,))

    # Texto principal
    draw.text((x, y), texto, font=fonte, fill=ImageColor.getrgb(cor) + (255,))

    img_path = "/content/texto_temp.png"
    img.save(img_path)
    return img_path


# ============== PROCESSAMENTO PRINCIPAL ==============
# Carregar vídeo base e música
video = VideoFileClip(video_base)
musica = AudioFileClip(musica_background).volumex(0.3)

clips_prontos = []
tempo_acumulado = 0

# Processar cada frase
for i, frase in enumerate(frases):
    print(f"\nProcessando Frase {i+1}/{len(frases)}: '{frase}'")

    # Gerar áudio da frase
    audio_path = f"/content/audio_{i}.mp3"
    tts = gTTS(text=frase, lang='pt')
    tts.save(audio_path)
    audio = AudioFileClip(audio_path)

    # Cortar trecho do vídeo
    fim_segmento = tempo_acumulado + audio.duration
    video_segment = video.subclip(tempo_acumulado, fim_segmento)

    # Criar imagem com a frase em tamanho adequado
    img_path = gerar_texto_imagem(frase, video_segment.size)
    texto_clip = ImageClip(img_path).set_duration(audio.duration).set_position('center')

    # Combinar vídeo, texto e áudio da frase
    clip_final = CompositeVideoClip([video_segment, texto_clip]).set_audio(audio)
    clips_prontos.append(clip_final)

    tempo_acumulado += audio.duration

    # Remover arquivos temporários
    os.remove(audio_path)
    os.remove(img_path)

# Concatenar todos os clipes
video_editado = concatenate_videoclips(clips_prontos)

# Ajustar música de fundo à duração total
musica_editada = musica.audio_loop(duration=video_editado.duration)
audio_completo = CompositeAudioClip([video_editado.audio, musica_editada])

# Adicionar áudio final ao vídeo
video_final = video_editado.set_audio(audio_completo)

# Exportar vídeo final
video_final.write_videofile(caminho_final, codec='libx264', audio_codec='aac', threads=4)

print(f"\n✅ Vídeo finalizado em: {caminho_final}")
