# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   CONTENU FIGÉ DES ÉDITIONS — DONNÉES UNIQUEMENT             ║
# ║                                                              ║
# ║   Partenaires et sponsors des emails propres à un événement  ║
# ║   (Rencontre Géopolitique de l'Océan Indien 2026, Madagascar PostgreSQL Conference 2026). Aucun   ║
# ║   HTML : templates/email.html affiche ces sections.          ║
# ║                                                              ║
# ║   Une cellule est soit un logo ("img" = fichier de           ║
# ║   templates/img/, ou "@logo" pour le logo Athena), soit un   ║
# ║   nom ("name"/"role"), soit vide ({}, pour compléter la      ║
# ║   rangée). Les textes sont du HTML de confiance (entités).   ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

from templates_handler import asset_uri

RGOI_PATRONAGE = "Sous le haut parrainage de S.E.M. RAJAONARISON Mamitiana, Premier Ministre de la R&eacute;publique de Madagascar"

RGOI_SPONSORS = [
  {
    "title": "Nos partenaires institutionnels",
    "blocks": [
      {
        "cells": [
          {
            "img": "98df6ca6.jpg",
            "alt": "Ministère de la Culture et de la Communication (MSK)",
            "h": 85
          },
          {
            "img": "dcbe4659.png",
            "alt": "Direction du Patrimoine culturel de Madagascar",
            "h": 85
          },
          {
            "img": "f7876e92.jpg",
            "alt": "Ministère des Affaires Étrangères de Madagascar",
            "h": 85
          }
        ]
      },
      {
        "items": [
          "Minist&egrave;re des Forces Arm&eacute;es",
          "Minist&egrave;re de l'Enseignement Sup&eacute;rieur et de la Recherche Scientifique",
          "Minist&egrave;re de l'&Eacute;ducation Nationale de Madagascar",
          "Minist&egrave;re de l'&Eacute;levage",
          "Minist&egrave;re du Commerce et de la Consommation"
        ]
      },
      {
        "mid": "et leurs organismes rattach&eacute;s :"
      },
      {
        "cells": [
          {
            "img": "08b2d27a.jpg",
            "alt": "Akademia Malagasy",
            "h": 85
          },
          {
            "img": "addee9bf.png",
            "alt": "Centre de Fusion d'Informations Maritimes",
            "h": 85
          },
          {
            "img": "74c879c2.png",
            "alt": "CRFIM",
            "h": 85
          }
        ]
      },
      {
        "cells": [
          {
            "img": "c93ce423.jpg",
            "alt": "SPM - State Procurement of Madagascar",
            "h": 85
          },
          {
            "img": "6cfb7465.jpg",
            "alt": "Équipe de la Primature - Lapan'i Mahazoarivo",
            "h": 85
          },
          {}
        ]
      },
      {
        "items": [
          "Samifin Officiel &ndash; FIU Madagascar",
          "CIS Madagascar",
          "Direction du Projet Pr&eacute;sidentiel"
        ]
      }
    ]
  },
  {
    "title": "Nos partenaires diplomatiques",
    "blocks": [
      {
        "text": "Les &Eacute;tats membres de l'Oc&eacute;an Indien ainsi que leurs Ambassades respectives, dont celles pr&eacute;sentes &agrave; Andafiavaratra&nbsp;:"
      },
      {
        "cells": [
          {
            "img": "004286ff.jpg",
            "alt": "Ambassade de France à Madagascar",
            "h": 85
          },
          {
            "img": "56e31e6a.png",
            "alt": "Ambassade de Suisse à Madagascar",
            "h": 85
          },
          {
            "img": "3a79cc95.jpg",
            "alt": "Ambassade de Maurice à Madagascar",
            "h": 85
          }
        ]
      },
      {
        "items": [
          "S.E.M. l'Ambassadeur, D&eacute;l&eacute;gu&eacute; &agrave; la coop&eacute;ration r&eacute;gionale dans la zone de l'Oc&eacute;an Indien"
        ]
      }
    ]
  },
  {
    "title": "Nos partenaires super-sponsors",
    "blocks": [
      {
        "cells": [
          {
            "img": "9a66a824.jpg",
            "alt": "Jacaranda de Madagascar",
            "h": 85
          },
          {
            "img": "f196d632.jpg",
            "alt": "Cabinet RTM Law Office",
            "h": 85
          },
          {
            "img": "b423f9bd.jpg",
            "alt": "SoYou Company",
            "h": 85
          }
        ]
      },
      {
        "cells": [
          {
            "img": "26920616.png",
            "alt": "Assurances ARO",
            "h": 85
          },
          {
            "img": "fae556b4.jpg",
            "alt": "Café du Musée",
            "h": 85
          },
          {}
        ]
      }
    ]
  },
  {
    "title": "Nos partenaires soutiens",
    "blocks": [
      {
        "cells": [
          {
            "img": "8b68390e.jpg",
            "alt": "CCIFM - Chambre de Commerce et d'Industrie France Madagascar",
            "h": 85
          },
          {
            "img": "cdef6bc2.jpg",
            "alt": "AthenaEvent",
            "h": 85
          },
          {
            "img": "92b2f5b2.jpg",
            "alt": "CEDS Madagascar",
            "h": 85
          }
        ]
      },
      {
        "cells": [
          {
            "img": "fc54b13a.png",
            "alt": "IEP Madagascar",
            "h": 85
          },
          {
            "img": "2d6b073b.png",
            "alt": "Chocolaterie Éka",
            "h": 85
          },
          {
            "img": "0da9f5a8.png",
            "alt": "Studio Sifaka",
            "h": 85
          }
        ]
      },
      {
        "cells": [
          {
            "img": "1d6492bb.png",
            "alt": "Savanna Spices Madagascar",
            "h": 85
          },
          {
            "img": "87474d1f.png",
            "alt": "Kamira Mode",
            "h": 85
          },
          {
            "img": "ab4e962b.png",
            "alt": "Cercle Voxmada",
            "h": 85
          }
        ]
      },
      {
        "cells": [
          {
            "img": "4fb45f26.jpg",
            "alt": "BRIO Madagascar",
            "h": 85
          },
          {},
          {}
        ]
      },
      {
        "items": [
          "Groupe &Eacute;ducatif ACEEM",
          "Lyc&eacute;e JJ Rabearivelo",
          "MNGE",
          "Chocolaterie Robert Madagascar",
          "Gen Z Madagasikara",
          "Sport4Ever",
          "&Eacute;ditions Mada &ndash; Madagascar Magazine",
          "Raoto"
        ]
      }
    ]
  },
  {
    "title": "Nos super-artistes, animateurs et mannequins",
    "blocks": [
      {
        "items": [
          "Rajery",
          "Iray Fy'Art",
          "Les h&ocirc;tesses"
        ]
      }
    ]
  }
]

PG_SPONSORS = [
  {
    "title": "PLATINUM",
    "blocks": [
      {
        "cells": [
          {
            "img": "2bf76143.png",
            "alt": "CYBERTEC",
            "h": 72
          },
          {
            "img": "e57eb182.png",
            "alt": "Black Python Devs",
            "h": 72
          },
          {
            "img": "6f641ee1.png",
            "alt": "PgUs",
            "h": 72
          }
        ]
      }
    ]
  },
  {
    "title": "GOLD &middot; SILVER",
    "blocks": [
      {
        "cells": [
          {
            "img": "@logo",
            "alt": "Athena Event",
            "h": 72
          },
          {
            "img": "d3a0cfa4.png",
            "alt": "Navicat",
            "h": 72
          }
        ]
      }
    ]
  },
  {
    "title": "BRONZE",
    "blocks": [
      {
        "cells": [
          {
            "name": "F.H.A",
            "role": "SPONSOR"
          },
          {
            "img": "4f74c311.jpg",
            "alt": "NIC.MG",
            "h": 96
          },
          {
            "img": "60b3e7c3.jpg",
            "alt": "Afya Bridge",
            "h": 84
          },
          {
            "img": "10dd6559.png",
            "alt": "Dalibo",
            "h": 72
          }
        ]
      }
    ]
  },
  {
    "title": "PARTNERS &middot; VENUE PARTNER",
    "blocks": [
      {
        "cells": [
          {
            "img": "c99c0e8e.jpg",
            "alt": "Ymagoo",
            "h": 96
          },
          {
            "name": "Mamy Christian",
            "role": "PARTNER"
          },
          {
            "img": "829db998.png",
            "alt": "Ingenosya",
            "h": 72
          }
        ]
      }
    ]
  }
]


def sections_ctx(sections: list) -> list:
    """Convertit les sections ci-dessus en données pour le bloc SECTIONS de
    templates/email.html (logos résolus en data URI, ensuite convertis en CID
    par email_sender)."""
    out = []
    for section in sections:
        blocks = []
        for block in section["blocks"]:
            if "cells" in block:
                blocks.append({"B_CELLS": [
                    {
                        "C_FILLED": bool(c),
                        "C_IMG": asset_uri(c["img"]) if c.get("img") else "",
                        "C_ALT": c.get("alt", ""),
                        "C_H": c.get("h", 72),
                        "C_NAME": c.get("name", ""),
                        "C_ROLE": c.get("role", ""),
                    }
                    for c in block["cells"]
                ]})
            elif "items" in block:
                blocks.append({"B_ITEMS": [{"I_TEXT": t} for t in block["items"]]})
            elif "mid" in block:
                blocks.append({"B_MID": block["mid"]})
            else:
                blocks.append({"B_TEXT": block["text"]})
        out.append({"S_TITLE": section["title"], "S_BLOCKS": blocks})
    return out
