import os


class Colors:
    red = "\033[31m"
    green = "\033[32m"
    white = "\033[0m"
    purple = "\033[35m"
    blue = "\033[34m"


class Symbols:
    info = "*"
    warn = "!"
    add = "+"
    delete = "-"
    unknown = "?"
    vertical = "|"


class ColoredSymbols:
    info = f"{Colors.white}{Symbols.info}{Colors.white}"
    vertical = f"{Colors.white}{Symbols.vertical}{Colors.white}"
    warn = f"{Colors.red}{Symbols.warn}{Colors.white}"
    add = f"{Colors.green}{Symbols.add}{Colors.white}"
    delete = f"{Colors.blue}{Symbols.delete}{Colors.white}"
    unknown = f"{Colors.purple}{Symbols.unknown}{Colors.white}"


class Collections:
    all = ["AllowedPhotosURLs", "UnsortedPhotosURLs", "BlockedPhotosURLs"]
    allowed = all[0]
    unsorted = all[1]
    blocked = all[2]


class FilterersPhotos:
    full_nudes = [
        "https://sun9-7.userapi.com/s/v1/if2/vLEDtwCTMwNEWlvbwBDTn9Ead6vS67T78Aex9_ogp1gw"
        "-JazovdfWsSzilybF5ofSIgmHT4w2HLUWApYlHIyzjCc.jpg?size=1000x1000&quality=96&type=album",
        "https://sun9-32.userapi.com/s/v1/if2"
        "/jdsezi7OMPmMWDzQ0df7Ga2RSk1QnBs4rEK7bDuXVXL7ABRLXhbrcPLdUIiyu01ai_jGcOqatDVCyvsBVhRIixKy.jpg?size=958x533"
        "&quality=96&type=album",
        "https://sun9-14.userapi.com/s/v1/if2"
        "/h7zrvrxuISlvFIChAFT7cowCqDGlCC0uZlF2DjzTeGSFU38WAr5GQg7eWEpIwTajSWvQPF2OdpIXADZ01XWYM9kB.jpg?size=928x1080"
        "&quality=96&type=album",
        "https://sun9-58.userapi.com/s/v1/if2/ZyjUHADvB2BLrzLcCC8eQEN2X-X99Yhvlhlcxy2fPz5P"
        "-Tx5OwemBZFU8sfTLJICbCDH_QKqUMAO9pyBGZhOC2To.jpg?size=720x1068&quality=96&type=album",
        "https://sun9-69.userapi.com/s/v1/ig2"
        "/y9Baif6EVRfUdz6dFRUXMvehN4UKgjtyikQpNEWMaUqWoHoni_gNiPP0D4ItBrnZOoH0toPY60d7sOAAC2-V3T3B.jpg?size=719x1042"
        "&quality=96&type=album",
        "https://sun9-66.userapi.com/s/v1/ig2/guIy4sb7Ssk5nM1N"
        "-OLkzvMwknScglLntKv3M3caFbu5tcC8yXuJzdBnpNgo3qgdOWhOqmWrLAIwY0PNgrZCdIz5.jpg?size=960x1280&quality=95&type"
        "=album ",
    ]
    nudes = [
        "https://sun9-6.userapi.com/s/v1/ig2"
        "/nzVzr_bblz_GLqccWEqpw4OrQhvsej5OiBu6NuHWLuBkmE772Fz1z7SBFwTp3B2uCv2bJ213mMMxUppnlmBr666j.jpg?size=1177x1177"
        "&quality=96&type=album",
        "https://sun9-53.userapi.com/s/v1/ig2/3nos_11PYF53C8tRDrbdhmQEUsW"
        "-g0L1P9LpDRUCI3UipsZGKNZ7CkvIlVYUoGYMeSuErUWnDQuhMDhLvuzt6ux1.jpg?size=1280x1245&quality=96&type=album",
        "https://sun9-87.userapi.com/s/v1/ig2/jEWNpsw8cJf4ftvBYZZP7ww42J4s"
        "-PqEldABDGZaqM9s8X1S11n4zLKpaUYk8rnGUSCqBpNy7E8GbAMAhJpAm-9j.jpg?size=962x962&quality=95&type=album",
        "https://sun9-84.userapi.com/s/v1/ig2"
        "/kAslQSDslR0ATDXZGwPnxS5lch_4TFgquadOOWdR4dz6P3lkDLasxNNmF80ypA4vGnmu70ebubrqAajFBKGxb_h2.jpg?size=538x807"
        "&quality=96&type=album",
        "https://sun9-13.userapi.com/s/v1/ig2"
        "/ibJ6BLZanA8Ayw9RmDjgUxpfAtGukd37Yxcaf0vSt7onl9gaVfTF3PRw3EI8QxDAAZ3yFjpdZX2Z9MU9S-UunGz2.jpg?size=604x440"
        "&quality=95&type=album",
        "https://sun9-71.userapi.com/s/v1/ig2/E8T1t-OtxQR8pJp-mLSjn2XazDOYx_Ndoi589iu-iZYVQC2O-voV5d"
        "-2OEerdMxbz2uQBPBgYKgEBB702mSrU5CO.jpg?size=640x1135&quality=96&type=album ",
    ]
    aesthetics = [
        "https://sun9-62.userapi.com/s/v1/ig2/wMb1f6FN576AMHaHQfLgJC"
        "-nwP_Prj6fq8CAX6zeJ18RgcsbkkhLIaITP_sD7WGSMxr29yoPO3fR3zxe-fwjpgLR.jpg?size=1080x1080&quality=95&type=album",
        "https://sun9-72.userapi.com/s/v1/ig2/CIHf5R2S1f8dKA7ATfq-FmLmdz4B6p6ZhxfYXZnPNhWtYc2fhESbBo"
        "-NDEdA9AzdxGBzWCTN5TX0pEbe5aaPkJeP.jpg?size=1080x826&quality=95&type=album",
        "https://sun9-47.userapi.com/s/v1/if2/E9ste0wa3mdjAAJLIpPRdc1rV9yQ4"
        "-jsVe7QYytEOLtjOpD5PaLVujrwY6EB43I1Jt2HKpnUZD3UslwwHHjYJwyo.jpg?size=959x959&quality=95&type=album",
        "https://sun9-75.userapi.com/s/v1/ig2/VETvMIeNJV_sglHKu4b0SrIoRndGjArsudYo7dkXJ302pKB-Zq_AnrgTZ4Gn0DTuZ"
        "-srTA3NpPbl4JzR5rOZ-pZn.jpg?size=720x841&quality=96&type=album",
        "https://sun9-66.userapi.com/s/v1/ig2/x0CE8e7-pFNgfpihzjKXLNt65-j9cDuxcxc-yDfopIoUWEJV4hA1R"
        "-N4jj0IrUuzA0yLQC3EBMWUP52M4xgy_l23.jpg?size=1242x1351&quality=95&type=album",
        "https://sun9-8.userapi.com/s/v1/if2/2JhxAFIv1ptThwwFGhaD8rdOccfLpzDarPle1k9sMEA64"
        "-5HWUlfdaRRdW0LAQvcgRHt9LRJH8jfbLDhluFicdkI.jpg?size=828x852&quality=96&type=album ",
    ]


console_width = 118

paths = list(
    {
        # "unreal4iksibiksi",
        # "sswxxww",
        # "boringcliche",
        # "sweetshawty300",
        # "ecstasyshka",
        # "c6373",
        # "ssssamura1",
        # "pcixe_ya",
        # "chainfor4s",
        # "imbabysss",
        # "savage",
        # "pictureeeeeeeeeee",
        # "devotskii",
        # "heartbreak2",
        # "frissxon",
        # "public190798808",
        # "mmmteltse",
        # "lovelyyq",
        # "pperfect.bastardd",
        # "dazzlingcommunity",
        # Nudes
        "yorksthebrand",
        "youisbeautifulpeople",
        "chloe_777",
        "ostanovimypain",
        "aestheticfeels",
    }
)

categories = ["full_nudes", "nudes", "aesthetics", "delete"]

TELEGRAM_BOT_HTTP_API_TOKEN = os.getenv("TELEGRAM_BOT_HTTP_API_TOKEN")

MONGO_DB_USER = os.getenv("MONGO_DB_USER")
MONGO_DB_PASSWORD = os.getenv("MONGO_DB_PASSWORD")
MONGO_DB_CLUSTER = os.getenv("MONGO_DB_CLUSTER")
