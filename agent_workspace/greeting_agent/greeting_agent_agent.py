
def run(task, tools):
    # Default to English if no language specified
    language = task.lower() if task else "english"
    
    greetings = {
        "english": "Hello! How can I help you today?",
        "spanish": "¡Hola! ¿Cómo puedo ayudarte hoy?",
        "french": "Bonjour! Comment puis-je vous aider aujourd'hui?",
        "german": "Hallo! Wie kann ich Ihnen heute helfen?",
        "italian": "Ciao! Come posso aiutarti oggi?",
        "japanese": "こんにちは！今日はどのようにお手伝いできますか？",
        "chinese": "你好！今天我能帮你什么忙？",
        "russian": "Привет! Чем я могу помочь вам сегодня?",
        "arabic": "مرحبا! كيف يمكنني مساعدتك اليوم؟",
        "hindi": "नमस्ते! आज मैं आपकी कैसे मदद कर सकता हूँ?"
    }
    
    # Check if the user specified a language
    for lang in greetings:
        if lang in language:
            return greetings[lang]
    
    # If no specific language was recognized, return a general greeting
    return "Hello! I'm a multi-agent system that can help with various tasks. Please let me know what you need!"
