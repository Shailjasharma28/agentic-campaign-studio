from decimal import Decimal

IMAGE_PRICING = {
    "gpt-image-1": {
        "1024x1024":{
        "low": Decimal("0.011"),
        "medium": Decimal("0.042"),
        "high": Decimal("0.167"),
        }
    },

    "gen4_image": {
        "1024:1024": Decimal("0.08")
    },
}


VIDEO_PRICING = {
    "sora-2": {
        "720x1280": Decimal("0.10"),
        "1280x720": Decimal("0.10"),
    },

    "gen4.5": {
        "1280:720": Decimal("0.12"),
    }
}

VIDEO_SHOT_BASED_PRICING = {
        "1280:720": Decimal("0.13"),   # 13 credits/sec = $0.13/sec
        "720:1280": Decimal("0.13"),
        "960:960": Decimal("0.13"),

        "1920:1080": Decimal("0.17"),  # 17 credits/sec =  $0.17/sec
        "1080:1920": Decimal("0.17"),
        "1440:1440": Decimal("0.17"),
    }


# Calculating Image Generation Cost

def calculate_image_cost(
        model:str, 
        size:str, 
        quality:str | None= None 
)-> Decimal:
    try:
        pricing = IMAGE_PRICING[model]

        # Open AI style pricing
        if quality is not None:
            return pricing[size][quality]

        # Runway- style pricing
        return pricing[size]

    except KeyError:
        raise ValueError(
            f"No Price configured for.."
            f"model={model}, size={size}, quality={quality}"
        )


# Calculating Video Generation Cost
def calculate_video_cost(
         seconds:int,
           size:str
)-> Decimal:
    try:
        price_per_second = VIDEO_SHOT_BASED_PRICING[size]

    except KeyError:
        raise ValueError(
            f"No price configured for size={size}"

        )

    return Decimal(seconds) * price_per_second