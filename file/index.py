import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp as youtube_dl
from word_detection import word_detection

# 봇 토큰
BOT_TOKEN = ''

# 인텐트 설정
intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용 인텐트 활성화

# 봇 초기화
bot = commands.Bot(command_prefix='/', intents=intents)

# 봇 준비 완료 이벤트
@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')
    try:
        synced = await bot.tree.sync()  # 슬래시 명령어 동기화
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# 슬래시 명령어: 음악 재생
@bot.tree.command(name="play", description="유튜브 URL을 사용해 음악을 재생합니다.")
async def play(interaction: discord.Interaction, url: str):
    if not interaction.user.voice:
        embed = discord.Embed(
            title="음성 채널 접속 필요",
            description="먼저 음성 채널에 접속해주세요!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    vc = await voice_channel.connect()

    # 임시 응답 보내기
    embed = discord.Embed(
        title="음악 준비 중",
        description="음악을 준비하고 있습니다. 잠시만 기다려 주세요.",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

    # yt-dlp 옵션 설정
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
    }

    # 스트리밍 URL 추출
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'formats' in info:
            formats = info['formats']
            audio_format = next((f for f in formats if f.get('acodec') != 'none'), None)
            if audio_format:
                url2 = audio_format['url']
            else:
                embed = discord.Embed(
                    title="오디오 스트리밍 URL 오류",
                    description="오디오 스트리밍 URL을 찾을 수 없습니다.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
        else:
            embed = discord.Embed(
                title="유튜브 비디오 오류",
                description="유튜브 비디오 정보를 가져오는 데 실패했습니다.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

    # FFmpeg로 오디오 파일 스트리밍
    vc.play(discord.FFmpegPCMAudio(url2, executable="ffmpeg"))

    embed = discord.Embed(
        title="음악 재생 중",
        description=f"{url} 재생 중입니다.",
        color=discord.Color.green()
    )
    await interaction.followup.send(embed=embed)

# 슬래시 명령어: 음악 중지
@bot.tree.command(name="stop", description="재생 중인 음악을 중지합니다.")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
        await interaction.guild.voice_client.disconnect()
        
        embed = discord.Embed(
            title="음악 중지",
            description="음악을 중지하고 음성 채널에서 연결 해제되었습니다.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="음성 채널 없음",
            description="봇이 음성 채널에 연결되어 있지 않습니다.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# 슬래시 명령어: 음성 채널에서 연결 해제
@bot.tree.command(name="disconnect", description="봇을 음성 채널에서 연결 해제합니다.")
async def disconnect(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        
        embed = discord.Embed(
            title="연결 해제",
            description="음성 채널에서 연결 해제되었습니다.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="음성 채널 없음",
            description="봇이 음성 채널에 연결되어 있지 않습니다.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# 봇 실행
bot.run(BOT_TOKEN)