import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from io import BytesIO
import requests
from functools import reduce
import unicodedata

st.set_page_config(
    page_title="Balance General",
    page_icon="🚚", 
    layout="wide"    
)

logo_base64 = """
iVBORw0KGgoAAAANSUhEUgAAAY4AAABsCAYAAAB9/1VBAAAgAElEQVR4Ae1dCcw2SVFGlCgoiBcSPPHAFaJ44a0rISoqCt4S0QU1SrwWFRUURePBSoRVDIqoQUMUxAM0RjCoqFHBA5d4gBdChETEA/G+H+eZrWprerp7unp63nfe759Jvq/nnb6qnuquqj6m5za3Oa4mBADcGcD1AG4E8LTh/gUAbsH0ep08vxnA+zRVdGQ6EDgQOBA4ELhcBKj8xVDQSLRczPfOl4vAQfmBwIHAgcCBwCICVPRiLF7RYikSeTgK+ajFio8EBwIHAgcCBwKXhcAw7fRAmWZK6H78yqD89e8lqQQLz2g87nxZiBzUHggcCBwIHAgkEQBww/BnRxc0DN/FUUJJ2cuax4Mk7T8sGA5Gf1eSgOPhgcCBwIHAgcBlIBAZjFcCeETreoRMb3FEUrpedxnIHFQeCBwIHAgcCEwQAMBRgo4wqOwfNEmw4sdgQH64ZDmOtY4V4B5ZDwQOBA4ETo2AjAp0dxQNxiYL1rIWkrMfm9R5aiyP+g4EDgQOBK48AoMWf6xock5Jbaq8ZQtvznB805UH+2DwQOBA4EDgkhGQUQZf0uPi9SNOxQsAGqjU1W1a7FS8HPUcCBwIHAhcMwjIricueH8TDcgpGZc6U4Zj09HOKXk86joQOBA4ELhoBAC8I4CPBfAwAI8G8BgAXwbgc+X9jA88JYM5w3FKGo66DgQOBA4EDgQMAgA+EcC3AnjuYCD+LuXaJ579PYCnA3iAKWqTW9m5FZPwkk0qOwo9EDgQOBA4EEgjAOBtxFi8NtbIDb9fD+AmAHdJ17bu6bDG8dAETT+8rtQj94HAgcCBwIFANQIAHgXgnxLKuMej7wXwdtXEVCTMTFUdC+MV2DGJ7EzjG/08ZZhbqPUvJW89kfjZQyR3z11fWc3Jk5E2oVFPVybtqetieDo5iEeFmyAgG4nYPvl32ccjAfgY87JeqoP1esYRyBf0kogcQxLT1lUYImAei7Knv/dowVA2MtBQ6Hs2MXYtv6mcz7oZQTojj+GPj99v4Yd5aBxvaMH4HHkiZaRKKRV27Rs1vEqbS9HS89nmm3IAfEhBB7zbEhYiI/Y7vrzMzUT84/3lvToA4I4AntXau1bkez6Ad1gCeyl+EGR8/MhzlvLUxJM2AN8DgIZuj5dry7Mc+0JluOXFTrF5B7byWzgwswevPPngRlvnXu5Fpl5DeRIDL0qSDkVupNdDNrky2A45guZhqqsMJYA7APhaAC/PVSbPi86w4KHHLQWDybYko/7LOV8PwHsC+LMFQLaM5iL6ql1YCeIeurZjA7gPgL9JlL2nR9fV8Ckekle5rOGTimK1DJZ4E6Wpx9msobc2LzHcxQfDxINvHTGeQjY8augcBiMlS9JBA+Z2aAC8LYDfSxWaeHa3UpsVB5ffHOLFw13p8DIkfXzO2YzNZVOisSpuGGXcEwAV97mvfwXw0VVER4kSO6r+IUri/gngfgD+5dygLNT/iiXGxMPZeoRRInOTTiAdrFVpluitjduEryV5arwYjTWOwKbTIpnNKrXYbpnO5dDIjMNfVBJU3MUphmGcCZHywqhPjIfG7XtTjxiNvXgEKpvP0M5RGw7KMT7ocNVwTzyMPRhTxSQXPrmEkRjUPci3m4cuCpPTD3u4zmY8ZO1lDQabGQ4x6mtoO0XeRR0B4A0dIw3S/LiF/jiuZzCNMGgNB0ceo8HY9VoHgLcA8JenkJCzjv8E8L4lAcRxieGwezhqywTw006az5U8+37MgAkXiPdyvcDi23ovHtsaL3sLPELnb+XLm08WU9fysqXhOOXU4RocirsuG3D+yJIsZefn2F6EaE6dcVciR840HOM6jKR701JZZ4sD8MtrEN8476sAvGUNOIkh8aph3uDJ3Xtj3noWf/sURjKX27OeHmWtUrAJOfegqUcZHNGtWnhNyTD3TEZcPUaRmxiOHcspJeviVC+Av01lyjx7fU5m+lwMwoi7lDHupJJpqqfZdHq/q1COCMnwv5vHvwrgDZaAS2wnXTvaeOJuECgT8rwUNoNi4ZcU93g173LbqSG0GC9Oe6Rk1fKswxSV0r2V4Yh3N2p9ew2T042JddMl+p+1JM/cGoesQ7J8HY0095UlGprjhfglEPYS/yUlRhNzqatGG6wLwJ/uhfkFOmZbQ3fu7TV9jfECjIaKafNRR6K9a90tYXflJKOhFlrOmSepMwD8oJOoh5V0lcbJlJTuqgqjcFmn5ZQVd1W5tthr2ZuGw8GEL3QCcs7kPBPrDjlABiP4HEMcj3Ff1XkB3N2Ut/fbe1hcOjkExJAeY/zXC4vqRXJRQufcDebleRMPPpJxz7WDX7Fl97jfueOSk+ctKd4BeI9ZeutUOfEz6afcfsvLGo53lmfd5RLT4P4N4BOEuEsKkh3SDO+Ul2Q6D0jDtuQv18J2Hr7a8iVKtlWp0PjynK+i0ZUGz+PyaVxar2pPquOb32oMySfpt398lvuOi5fHpAKyclpzL3R7aSql766gxGsu1bnLuFguDU7Yi+MySr+lfLY7Lo7z5UT+8Z7tsdgPS+VuFjcYjt/ZpeTKRPH9jreKQYnWNiiE1YDLyb9laqaxsWd+qt+PtHg0KhV6PcHjseWV7sVIxdufp6jkf1UZ9w7TU2wPpLG4a0b5FCeEa0NrjCK5XrW+pvTEodDXY0HcSmYLw+GlcW1/Uc/d8uW+T+D9dc5CvjUuo+a3rKPQkeE23U3aTg0dxTQA7usEY0/Jv8YyR4UXEedWgLY83gO43bBp4D+icks/XxqXcY7fjUolOa/roV+8oxI+qbhFwzEYpjWL+1T87IhNToRguUYZVRkqD85MGzlJKVxbnnU1HA1eevFluVqMRGaUebPRj+sC8OtOQD80LuPK/AbwDCcYe0r+MiuIqCOtVoIsu2Ea7wmWpnPdDx3H6/33wuvODQ2kaDhWzpFzmN/Fa5PtkQ3s9T+krmF3Ty3dXafWGka9XXeiieFqMh627wK4E4D/rQWRBsvmv1L3wzc13ggAp3wu+RrPspJhnfLRZYqKwh6+PfJkLbQyvN+5G4l4W5Xkjsl6e5lU1p4razik43unOrTu5JbKVvk0eM9KR5a/FlpkWtCzduUarbXQlMvTsCZVvVEiV2f8vMF4jXKz5QD4TBVmZfgMm/9K3fMLfJUg7DnZE6QjWeWyeopKBT0c8f5qB/M8w+q2mvdcYWREa8jv2lkbRghZBd+geMgvPcxubcDKsWEkR3p6G2aPIeB6gWsUaPldc++tdysvvYGOmcyGnZU/UtORTJrPWYPdrvMOR6ZT6V7yRUV9XdSZuw115XRgDz7d98C3NKDhZFiPN9plTtnS2TDiSSr5Rk+RRqOrIYx40732nnbRzXA0jHrGaToPsZbfNfcNDkSX6dIUzR7+Je1klOjchsspraptuClad/8MwG83ALqnLJ8azfV2VYLDlw6/ysnsF55b6A2KpXorrIe3wcur9opT5TbwoaLaZCHa0tiwVben4fCc/BuUn4JTE1pe19xHDl1N1dmR5xo6mLem8ihNaEfyGYUouvjzt9fSu+v8AP6ryP6+I39IhqA6RUVPs8siqAoNwC85ISieua/lbhl6FLbwlvT2e9AoI4alhclXpuqKNjrUimEzxWNpbBgJdRkFO6cgJ+t8tQAyneV1zX3ikNElMpp2vdXQuFRxIj7QMsTxwEHPFQx2DW0XlQbAXT1I7CwtPy71xtH5PF0VIIDbA/hvB99/sIcG0LAmEDyrPdBPGhqmOCimzaY5UrgMIyLPBoDViiRykmqa5cSI1mQwaVY7YA0jxq6zBVZmiW36htXk7YQWAC9Kpso/XPXxOUv77u6Hl9o+KM/3rmO4C4wfmeJbzXqt7pixgKIpMK2nFD4+LuMcv0sEZuJOqnBrMHGu0ZCtiXddU0ePNKKQ7BvnufvVTo1z2mc2NZaRfe5xD3qJhefq3odVxg2j8DB9e2zDVRQlbLDCnkawZdovFG9Gp6g2UXwAnupkYnVni0Tk/rlCphPv1F1xxwzO6RgV0e5GTR0h4QgsfrFV+c6Fs80BuYSZ56vbcsPId0ZzLwwbHJEw4gLwkAxGucdP70X3LstpaIw5oE75fBSKaZSTIWVPoC90Gy6/5dx6PbYnfq1lNXTyXexka+W3Jp9p7zWyTa6n1GQ0aVYZDq41mrJqbjd7Wa5Bz00cUQA/VsOASfPgGplebBoAH26YvYTbXyfY5ryicXqCXwUE8Kieghi+9PfeTkB+qmf9rWU1LNrGbHIb7w2cT2+lYU2+aPoxpi33O3iHa+rea16nTLkRISm7HHiZ52sNh51GzlQxeTxR1j1l0bDJYjLykXeCJsQWfnAb7p160n/2sji9Y4kA8F4FAPYWRYXGl5i0QY579eW4c36N6+stb2vvaYicAHz+2jp75HcqmRKLnAbUEzqTiqgHvXEZDaONzRROTNs5fovnrlOyJXlpXJibj+nVBJXhWsPh2ThAkjaZKm2Y9pyMXgF8aCVemuw3Y9wv+rcAOFl8Gj5I8vbK7c7Df5YX8fTFKzUadwHwF0L77ONFawQ2HPzIrwx6ru8VpZ1bHG19/tkePho6Si2P/P4FRyKbefcNmxFI+2b0eHDfKm20a3BJVsVp26XMUXzWANXwuodtuMbJjFjL/qRembQnAN+STZ2OeEwNPheRxgA4m/tM8767p/xWCEcb6nlxofCOAH7fUPrAXsKQXRSebbiGjO633+jhq2E+t4Vgjv5ujDuZh85U2qG8sxzKmKJlD88aDGlxlOAU9MTJ9ODR0AaLBs9Tt6aV9ulkef51PQAvdhby/krDRYfGaJD/2XBw2DHw505gTp38a8Ro3CIVc6rqTRJfK7xXL0EB+PRTM1mo7wM8fFGZF8raIkpHIqums0TGXvomU68enPaeVvDwHBuzOGXnBHeN4ag+MUBoWjW6UVkKZhwVe3BTWGb48cgQjawMX6u0XHQYeSwzYMjcsLD8M5WgnCPZE4VG/UzoaPgA/GxMTE9BmcX3uJpT/y42RHaUFN/OxbyePNG4N41EGqbYkm+bp/C4xGfOtarZFEuKZ6eg1xgOdfJqq+RaGt/Mbv1jfs8xLDFd/M7KrC8BeFiccOH301K4X9Sz6D2H7MtRw5Hq9Oj3eD2VgBslrkYjtTXuRT2FA+CvdgLID+X4Gho6vbrJfKymbZjy2YJdKoFZZ1Qa49C53ZT0rvZSSd+gcK7f8K9pRNTwxnWVkncKuarMhBxPPeJ1sjVLnjQa5AvAT8xSlx98RozHRf2OjAZZzTbgwXt/vzIWZ4n9URGc7qBSo/E9GWrGkUkPIe0Mj/vGPImy446VkkzZeemFnvvimtSiARGevLQmjWaMV+n3UK93SsVL42SHTokWG+f0nqtHXk7iZ+uhlsbcfTQ17qzy5MlLRuO2AHjydu3FNdHL3YYrndAOFRc9BwB/XYvOCdI9l43SNEA1Gt9YqPsjcg3Z+3w4m+oxhXpOGfXCmHZxCLiAvOjJG/xOSXOuLrbHLM0NtHZZTG0Y5eT4yz0f224sx9LvBiyKC+K2rhyRmeezI0tsWbn7oY16t+Fmqt/8cdEwAvhIJwW/lsNk988TRqOqgwG42QnSVsn5Pd87mM6jRuNLCxW+oqdgAPxGoa5TRt3b8iU7VcYP8tjnpXvBcQ8jD+KW/Rxpg7JZdIZKuDDuRJsIXKMi6b+6c7CmrblGNDUFmjSthsNDv6nuZLfsQ9nRurabYQPOTU6KHq15Ly406wHK8yJA0onuoxnOGPL0yTcTr5qNT43GVy/Q9A29BAXgLRfqOlX0wyxPYgCSmxtsutS94Mkh+R6upMI326xraaz2slOY8JlxTmrr9KarctosfYPh8E6deQ2Thwe34WjYhuuhZ21ajtSr20201b+m7omjZ+W66/vELoxkJ80xAeA3a9DZKM0Lh1HPm4uS40L+KODh2PTHVdR31xxP3ucAHlxR35ZJ/gDAZB+4OANNRsPyLzvs6G2d86JDMFF2LcrG8tV6f4INBMWpkJjuBhxc/Zv1OQXfYji8hs9J0qrk3HVV60jfzVlTcfdjLOvd/E54T9ULZsoEgI9zgtUrOQX6psZojMIFwDexl65xEV15WBsCePpShRvF89sij7T0y7QFsXHPk9ty4nuZouFb7DTQ57gmu6ESDs8STW6FFmPA34Oi3tqIVnu3Qo9dl1zCILtLMsWrPnPy7Ma58f2JJV57xy/2JwA8fdtz/aBifDGhKNx4XtHVaJXZhq/decBNpf1J1p0wGqktt6n8d1fae4QAeOZV7fUq8RL5FnvrHw+ZvGNMu8FjsZHHeT2/xYg8YqjvlAuak7UOpzKjbFyefA6Phnpr2wXTuU56bXiHpekIeSfPrrVDaUsejM6ZtjjycB7zQj4+JdfOdvlcvNL4LUnXgpllTITPjySd4rqZdYuSpPc3TmEMZ1L9eGXlXRSI8t/wUavv17w9Q3mBjgvaxcbds04tS0auNCKbLqhrfQwb1jealKatU+rd0lhWTy1Kn4sdv1IXcI8ElHen4XB9PrbB+JV43DouqyMBtGzDvb1ifBFhxjJO5pC9jAwvv33R1lLj9ATpMvPufBHrDYejzH+6sm4ebHgHL2+l9AC+ubJuTdbtbCzBghjwDVguZK+SYYnP2rhByXAUxQXF7kZEaRClqXjWhk2jaa1TQ+Gvtk5vuuqRYqYPl+prdig2NhxbGuISHk1x2g7iEMD9nAW+IC5j178zc8PuBbMUkwB+0gmeJ/kXsU7xbsM7Cc7pkvuk6F7zDMDvOJjgyz7dvAxRoJzjZufLvu+whr81eUVW3dYElJZG5d2sOLVeDcUwOsRenbRKhg38rxplb2w4qsGRhGxPrX89nJlkOxqmjp/gZOSrtT3tPsw0OIJZ1WCXGJSTZ1/qBLAm+QNYtyiisRMAeCvnEeaj4VniwRPfcJjZ8z3ll9LKqItTFauUQqmOXnHS7lZv7VV6Ms5PsR1p3l6h8EQHpqTEPDxXbcPNTDMXeZf3rVrPc2K+eFq7WF8txtKGi2VFkc3TbUqTOFuUW+uVHLkCeJmzwG6Hqypvm4SFBtdltKFEDzuM3hXA3ztBzCXnq/v3Z9lDAjbgcSgv6xuvzmVKPN9k94J8ZyJRXfbRVyhOa0Lz4mX11Maa+nrlbVH4Fkmlo6UczXvK0DkyqeqHLbxbDE9xX4sxnR4nPZOddbX1pNKtWFuZGQ4A3m24r07RtMtnmTnRbqMNyzSADwDwj85GESd/DYBxakka2CgwAJ8dJ1z4vdkH4AE8c6HuOPoeFifvvZmaotySQ2ZvmadOL6PGGJea32GruHN6ciz7DHx6D+1blKfIvwarc6dZ5IXy8I5kyH8vOa7AcjY7A+CLnYA/pRcfm5ZTsK5VXk4LcTIq+BsnoJqcL7S9rYyS6JWMDbHyHQ0tg+GTWmivzeNcAH55bbmpdKJwOTW1i0XwFI21zxq95rCjRaaHrJwX72tp65Uu46jl6Kzahus8xDBX1ymez7zyGNcGxR0ch7is1t8tQKTqGhzln3OW9Umpcnb1TASU2ra3yWjDMg/g7YYXBH/LCSqnoLh+QY+NRoO7ht4JwO86yvm34UNTD7G09L4HwHcpPFeTERP+uWuKV9gU0MKP8xjwKq+xkQ7K1HuFaYoWw8H21EJrS56GufvFbbgNZXrx7Zm+xnDwPSDP1X0tz1O5pJ2tsQC4HYD/cJTVdYNMS/usylPwUhYba1UFFYmcHiaPC6FiGUdDAD4fwD85BPPzAN6lgqxVSQB8u4MmJh3XajyVyqhN3wxetZ4hhthD8qyTeGhfStug/IPib8hLvheV2RLNNfHSdlOOWgn7omwbyyzVt3XcItYN041d3sOxMmwAYaYz2a+d5XTbIGN56XpfmKIir6Ejdq00UxiVOYBnVIDM74HfBcAHF4xeqhh+yrbrOxIZVsbHMmWUoiP1jB7J7UrlxXFDIdwMwKvLekaDx7q14fDs1JnsOGo0HN091lhm/J04MFTEWAxm8+a27MFweBeRi5WdILLGcLjIsHj0uncRcGviMOpVGjgd7iznKzXvLkPxMHOez6ZKoQQIgLcfPlzyROcooiQbHuHx5aU6e8c1bMP9uVoaRG46yuBWz6JScZTLc6Y812ZtpGH0M/HIGw3H5MiSWtw86RYctRz2E6MY1yejzlzevT4vjg4anJiwvhXj0/q7EdfZ9C2AlzuFcF0rzSfJt7A4N+mIJyEoqkQOKOT3Mn4KwF86wf9D8ezO8slFmT7zkPzFEfvJn3JsiBr7rh7yoKy9e9e3NBxeIzYxno2Gg/LabJS9YrdYcYPKCT4a5WnHtWmXePK2xZmnn+xAjocN8pptYADw7rWASLp9b8PlfG6BoRkADrw3SyoL4h8P4FGyJkLlYv++DMCH9XzzupUZMXYFiGdRdyvVJR44T7Tlxamp7oa9Qdm6Dqsr8WfjGubrZ97miqmbTY55aFBCIuoxmHmxilfjCMaWfa77JcPhmaYkD90NfkMbmjlS4uh5MH6yynaX4cL+6FlH3CUTOyWq4TCzl5ZYkWG7jjI222rbYDjYIYpTDiW+cnELI+FUJ5wp1pUKtStPDcrD8pjdYtpgYG25577PGo6GKaIsRrk2VvO8YSQ34wnALziB/oQa2s6SpmIHU3dv9iyMnqnS4ZiT+zoby3emSI1GGSyy69RUXGej4eBay2SaKC7X87th4Xi2i4X1LYyol8RDI724eLvEV0J+S/Wm4pP8CY/e6RwuoLce07+Uz3N0CvmcKVnFs8Hod+8XYpRT8ig9m7QZznw4t+G6N8goZpuHlV5KN0WwOUM7rGA4XffxpdaViHtWNOXG6bfnAeC7Jrz+Xd5At9NyPe4/zcLXaDhIH98hWdVmpF0++1Z2q/9zyi47RSFTetWFJRLeaPGpvReDwR1vOkpMFF39KDn6aTCMTR9ocvDMTRqeq2Q4vGUlMaqlPZWuYXF+dlQ8gE/0AMI+n6JlF88qRhuzebpdEH5BRADgwvwlXJNtfysMB3nlyMO91VkMRquSzSofNpeG9wBSMuNc+40lAyV18b2iBzaMmFJ12mdJg7ww1Wzz6/2mswgNbSc5kpL2oDTXhJusxw7y9o7mZnqz4RSLk+78rFap4gkteUHdh33VBF6BhA2HmdV0jq3SvKeFvMKpqKGDivZmOdzx+ngkIvPXfE5j4R1h2Po5NZJUqsrTygVpW5fekzduUOCf0s973Rqt6XqFM2VE3hrklCxHceoRNhiOJE0Nnv4m67ENhnnmxADwHLLKNrP5S8lNsq5scJt6Jk2EX1AmAA/vpTU2LudVMawNnXZjErPFVx+FMxiPc33/PEu8I2K2xbTS+YurmMy9x3Lv8buj4fB6+t31lWAcY7j0e4IxgHsuZYji/6yHHLqXIUPApdEGeZntUOlOzBUuEMDPRg1irz+/LxZDwzTBuXirbqMNC63n4ilV74xP50kJLDM5JRTLfu3vjoZjD9twH5oSRuHZbLoMwCML6VNR371WBpvkrxxtzBZ4NiHmihYqh5nx+yCXcCVP36Si2Tnxbg9zZ6MOTrHVYDzbYtowIixuHujZDXsYjoZtuMU36lv5q5SP7Saz6TIAv2wTVNx/bCu9m+arnLObNdZNibpihQP4mIoGsock2dM3h07j/UbEqfhpfulxUGqll11PRT/rGddlKpXsZKQgo0GvNz6bd9+qy1XyZLGerXE0jA43WY9tWLOaTCnKNlz2sdprn9twHZ7KTJhbNbSrWK756l5tgzlXul8s4V87Oj0h8TQas2mbEg9x3KB4z30IIEcZ42J+pZKdbDFtoH/T7bcJfLk93HUlyvBuw52sK8Tltf52MXFr4gkdAD7ZWUb1OXWtPDXlGzrdcyoZOQxHE8K3ZgLwJ5U4nzvZVy2xWancTsEHvfTsuxpLfNj4himIXvxNPP9KbMOOsYYpHNLtntKzWHnvW5wNW4eMqDx4z9YVbHmt94Ns3KPTuK7hG0M/4GGEXweMyzj7b6dADsPRKDEAd3c2lnMmv+cSm9JuqLTPdTVPTZV4O7HxoNc/8UZJW4WSnfTDhgXxSf4SHr3iKniatSNbd8PW6dm6gi2v9b6T4XjtjNnyg+I5da28rMrnFMjJG9wq5naUGQAPWLyEa7YNNwejGI+ahdyefNNgcNojeNw5+lqfS/msZ8tr/DJlisaKdaQwZ+7sv8rPzFil6Oj5rIPh8LazTUZUHfi4twqhMnxZTzl0K8sxTUU+D8PRiDyA51Y2lHMne4qXRfHCtn4fgqMbboPczGBYvkV5107hemRGBbg4tSbrjjnjNeYXw12zhd7SN1lUtzxved9B4Xr5XMS4hd9GQx3Wo4azqR5thVFx/4QWOjfP4zwv5zAcDRIRJfTiTCOhQrxJOlaP86XWltG8yCwGhIqxhxGh0uRiKL8rvYkSqBGlyI6jgzU8KR9uoyeY0mAGuSrdEhee2zSF+7Ng2UKr4XP8DHSBpxiDMCLTMnqF0h7i+pZ+h9EPgM9y8MFy79WL9m7ltCyqdav8GihIGhkP+EtdyfntqwKLtK0HSSehMaHy1D/yToOpvxlSObOjMM9ZlNsS9iJPVeKWdvJi+SG/5OXkU0JLPBzxBwKrEWjYF00FuMtOvRqMjgUsGAxiSKXi9j47kngUdSBwIHAg0IaAKLCUN1x6Fubr2mq9urkqDAa91MPwXt0mcHB2IHD1EZCpgpKRSMVt8jbmJaNdYTA4NXMY3EsW8kH7gcCBwK0INLw6T0Nyy4FfwI8vA+l3vlNGdtw6euB1IHAgcCBwZRBIabrKZ9f0ot9gPPlBnpLBIIzcynlMS12Z3nIwciBwIDAiUGkkUslecK1BKHvm+aW3pYPkuI5xTRvWa61tHPweCFxTCKQsguPZNeFNm/WLpReQuI4R9mtfUw3pYPZA4EDg2kHAYSRSSZ99lZGST5suTUcRl2Md4yo3hIO3A4EDgSkCK9+GpdK8Uh62vFGHOMEAAA1tSURBVLTG72EvjS7UkB7vY0yb1PHrQOBA4Koj0LgdV5UmQyrYi56yMmsXt1jGFu6rzhu66u3n4O9A4EDgGkRgUPpUgGsvTudc1FvQYixuAPBsJ/OHwbgG+8nB8oHAgYBBgFNNTsWZS05vfdfGY4WxIM+7MRjytv9jB6L4N5sqFJlq/GONuMOtTMkxDafl+MfdYjP5mbqyLy/K2VIsi4cRvpHk4RTe/bXCUjmy+WCkV9Pb0MSTTuVrcZRr8jFPcpeboZ1pJoc7mvwWo2S9LF9ps7TrveE/0BHLSfOLLK7XvDWh4UMxuiGVz0FnkHeBTm5Jn+FheFVZaXh93MYAvINpL++VoZltiWXM2jrTW55ycrblGqx4hhzLDTKJ0lE3Jus1bYPxMwyELp65xvhSHWw35C9MeUf8pPqk0hVkZOk+yb0AMPDW5eI21aQQTsJMohJRkFSK3pGFArIbg0H2hB+ljeHktGIxjjZ+8hU0kXduwZ/TjpPOOXQyHtzHa1KPQi3l6XoQG//7SHoGDxea7TfKX6F5NZROw/QxrTwRtSS3m7WMXDjww51uvFL1WlpfomUIhqV6JxgxH/GRel6p5WgYYRLySvpSwP40Uxxaroam7rgs5o+NoR4TP8GaZUW6IHyRUDZ/xGXb35Yni6lNo/dsK4EmAJ+nEQDeX3myoeGPeSd4iKy0/XGTyiQ+Koe05bbSz2ZNDN+zD0KJk6SkB360vogupgt4ahqGAJ4phfwrgNvKM/sJ49kpv1opabBlnfzeKAdD06pbWvKkFd6aOWn8nIIiDblGssQcGyCFdxYeShiJ92fpnyh0o4Q1TYhPNGYqOyp7VSaaJxj/AQOdynxdii4TTwVNRf9wLQTABzOPeHjm8fToFaMYQgeVsuyak9JKetUYsMxi54k6ePDQovIp71HW0XOWT8OZwiiUJTyyDF6BB8UromFUMlSekp6BPVWXfKqxZlzx2xkDvVbJ6OnCDJWeySkPBrvQLgyd9JD1GtsAcdEHCTo1Kij0iFfyon+Wp/AOGIDvk0L+E8DtlBYbDmXYT7VOFHDUdkO7tfl5L2WogWGVpIdt27alcJRSxPekTilP+8XMAEu8lQvrm+Et6f5Y+A/xgpk8njo8UbvJ8suyN78SykiJXhtSeT9wSwaGt7c5/OWIgnVZRdNCOxsRlUTWa9mSl5qypbGTN3bIMdR8ovS0c2hHDY3e5GG+4CUyf9Qgg/KLDNEElyjPWB6Ap9xKFuhB3V7KJqb2CuVLvCo5S6saM8ZNlLTkUf5nIwnG6yWYaPlWYdmOHcqPFFEKIy0r1BspmZkhMzKDoctOEc8UgDEeQaFoXhuadBMDE/VpNVY07HoFrLU8a4TMsyydUR1qaFShBl5NWSrTEAfgd4WgF2q6VGj4tLhzalSvGT9ajrQBdSIpvwnekczHNs42pwXH6VnuwLsanJl8ovag6QLdhq63AfA/Us9N5rmperwN9FrMNf1ZQwNETHSP31RmHPpTwc/mOZcYF8EzH0cSnC/sYSQsX1SyEyWxRNO54k0H0g4aGqRR8lSqajhGpRh1hGQnyyg46+2FBkz+jSEK0zPDusaLBNgXKUYmnSpdJlEP33q0qnxsnTNFLHXTY6dBovKYGDStV0OrEKVTW6UQFG5kCMNzLUfqtQZHecgqV8mjsghKxtJky9d70x9DHo2zoUlHxRhw4D0VnvypMrS4BmOp5Rk52Wm7wK+m0zAaXahxmvFq0qvhGL10jjAAcKTB60maLhWyf0o6Bryn/IOTlMqjzyI6Z/1cyiKfbE8qU+vsBFxZpmCr5Mz6kjFE7IcBc6VHQ64BaiH8uJOUbUeiGh3aomk3QUZa3lnCCFwleOuQIwTOLeb+tGFsRQcb8kQZngV8R6UGiOBtMbs0ZsXLKkZVGmpoqLwnHUGrN4aH1Wi+pJdqO4RiyBEGMI40mD98fnZoW2owghJiXUJ3kValbU0oxkKhIw6KE5VcwGJIpxgx7ahA4nojjNTQBb7i9PytFQ912akQHTFNFIDQSsdIr5lisnWwTE0ofJUWa60ynPFnyrGKKkenVdxhusaUEXgVDKziH8sH8IEm/UMsX6l7YySpL5Qutq0ZLza/caKCg2PjU/emfLYVXeDW0MpnYoCjfkGMrCGY6BoAjzL8q8GyOFl5aX9UvoOMUvSf9JkB2PBz5W51OqrY2E4KfGVlUaMMCp3ZjUKjMlRlHDqKUd6TaSJbtSkjTCVI2ar4Q2M1bSV4xFzTMK1Fp64mIwqjnMeRklF8KVpDfYZH7bwazjxIy5Pem3oNif+/SCvl67RC4Enza2gxUoVllMzECEiZweOkXEw5lo7c/cSwaV4b0vAZD9eWQ+UWjKLQoh5/wFrLihRcGOWZAqlA1cHTaR+N1lGt5ZVpNL0aaqYPih7Al2gBAO6htOTCCHvNGjAt5NO0E2OWS8/nmqEinOgR0y9CXaaMSVs1C+OvUVpMO6Xsbd8ZZWLKCjLSvGcLpfGokjA0XolbdprFRnY28CsqNqPCUbEZqVB5aOekx6KeSjASJm3WgzWNPniQJMsoRq3XekVhR0m0MH6d5LVpSadVLjRw6kEVaRUFadgIt1l+LKSRYmTmWccLJZqRgS1D+FHlG4yryTcxdJJeZcFk6lVaDEz2cMs6ZvTFtNjfgqtiqQXFC+PatwPWWkY0FaTTTtZb1jJtyPICnaZ92jT2noY5eN1GSb5e6SiF0gaUB5Y7wzvOHynflrZCWVCG9k8djIkBNhiSxmC0zUhpUr95/jyl2/TBkTfjFNAQ23YT+p3mPWtomLcCv9T7ix1dpBqB6WjaqFQuqpzGhmyUcWiompAdIFO29W6Ct8S0xhCNytI0+EnHNfSlthaGTmbyByUcKSAlN9AqCkA7r52eqXYGhjpU6SRHFFppAaMwyiOvgo1VrhOPUuKVR8t/mGakQTPlKH0T/Blfe4mBpLeql44GrHwDrlqukV1wGiJDQAeAiiv8aV4NjZIjHyGd3M8UHYA/EiKfr2UshUNZahzZt4NyzuUTPBSLGd/MJ/SFkUOkA4Oh0zpMOwoGWIyaOm92tMVRlz4P7W6Yyr2rEmXbm3mmI3adPWCUtqXgtChNuwijBmN4uYhbNigqlllD3QW4K4gwCnf08ow0tGFqY9Oo0OhNYw87iywppkMy7wS7qCPpOgCVQ+hsLGtY4CttLQxGJtO+UrSGPBGt1vOa0GDT2XsxPIpLToGoJznx1LUc23GpbPhclI6WG3iQuJmhkeeK4UQBRDhPylIaNLTGPFagKV4jOmfG1rQPqwyTdCoNcWjaZ1CQcRr9LethuqPo2/T5UpiisyKPymfWniLMtf8ExyQuO4Ut00Ty0Pri0G5ksQvj44uykYxCHzS4anmL+MZ0n+x3JRDKyLnDK2ssVODi0SjOqrT0N0MdbVilGjyySOndGJVrF/tm3m7UoLXOifKNFEFqa6Gd0qBCVe96LE/pYTh0zqCw2LGjOHr49OJ4Be/Ypkndc5pS8jBIKuWo3vByoWCfxChSJE+zdUflWUWgI4KZAjC4JA28lh/JZHI6wFCGHdEEXg3/k1OtIzpt+iydSoeGUfuctA1NY8NBhtwlqVfVlv0I68U6tL4BKx2lsL5gNAVDdbrsiFDTp9asZu1I6NJyUlNbs5FCpF/vSlqt3JR2ea4zCorXrI/a9Ge/F0AURCV6LyHpIqChQ54dsA0JsIpCq4kEod6SNrJJoxdZWmXNhq4KWIuiwg7GRuthqAkkZDmTdJa+zNbCoJCkPGscamnVzqnkBO/Y0pq6jzrqhHZNL8pvCSO2u0n+yCgrrpbW0NGlDqV/pvyG+ODtUmZKWyo08+EsT+u1C9cTfIbyLOaa3tI58ciVSNKUqt8+i+QflLNNY+8BPNKUn7v9jijPTGnb+Nx9RBvrIkYWJ8o86BFDzIzvVDsyuM76BWmK6h/rGTaSPE/qsQZL5TNxKKTvGrKmzlSO77M/F29NvQ/LwCnvOaogsGw8k457doBOQIBpsEHJGsURGuzQSNXQT5QASWTnMHms7IjtTIlZtqJ8YfSgaZa2Fmo6DYUWpSFHq/Ki6TRkW5zRoGWnQoNL6KiZdFwLSNVLjJMYiTEIXqUSKaOHSZ5IicwUbKQkZrhYmiVtilaSwL4y6SdCpyonQ+Y4+psoyYjOyajP0qD3pn2y3Em9msaGAH7cEpC5/8woTzCq9nnNvUxJUYbxRfys0bAj9hnfpm2kRvjJNim4a72jzIeNJK+RB89U+s2U1EQWjB9otO0r0Kt5dx1KZ6fwUgJQYHqFFCjroqEoel67Bq0TcaIk2KhDoxF55J5lMZN8xJV/k5FAjlxTVzI9t1OKsgnxhubwzJav6UvyNfXq4myWL1t2fG/KCfjFaexvk74FozFPSoFaTFLxpMHgUksrjR3bQRVGhoZVdGbwSsraphUe38/wSdpTf3ey+YxMquqwefV+CSdR8krLzAAaGkbZGCyLNBn+KKvbmt/vEtHGumdtvLYeLWu3oTDOuVR6MK2jERogGgidF2TDr+osuwXmIOxA4EDgQOBAoB4B2WJGi6p/nBqhBb3OPBvj6ks9Uh4IHAgcCBwI7AmB/wNTGaUfIJ1eQwAAAABJRU5ErkJggg==
"""

st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="data:image/png;base64,{logo_base64}" alt="Logo de la Empresa" width="300">
    </div>
    """,
    unsafe_allow_html=True,
)

EMPRESAS = ["HOLDING", "FWD", "WH", "UBIKARGA", "EHM", "RESA", "GREEN"]
COLUMNAS_CUENTA = ["Cuenta", "Descripción"]
COLUMNAS_MONTO = ["Saldo final", "Saldo"]
CLASIFICACIONES_PRINCIPALES = ["ACTIVO", "PASIVO", "CAPITAL"]
CLASIFICACIONES_RESULTADOS = ["INGRESO", "GASTOS"]
DEF_BALANCE_FINAL = pd.DataFrame()


st.markdown("### 🔄 Actualizar información")
if st.button("♻️ Recargar datos"):
    st.cache_data.clear()
balance_url = st.secrets["urls"]["balance_url"]
mapeo_url = st.secrets["urls"]["mapeo_url"]
info_manual = st.secrets["urls"]["info_manual"]

@st.cache_data
def load_data(url):
    """Carga datos desde una URL Excel"""
    return pd.read_excel(url)

@st.cache_data(show_spinner="Cargando mapeo de cuentas...")
def cargar_mapeo(url):
    """Carga el archivo de mapeo y limpia la columna Cuenta"""
    r = requests.get(url)
    r.raise_for_status()
    file = BytesIO(r.content)
    df_mapeo = pd.read_excel(file, engine="openpyxl")
    df_mapeo.columns = df_mapeo.columns.str.strip()
    if "Cuenta" not in df_mapeo.columns:
        st.error("❌ La hoja de mapeo debe contener una columna llamada 'Cuenta'.")
        return pd.DataFrame()
    df_mapeo["Cuenta"] = df_mapeo["Cuenta"].apply(limpiar_cuenta)
    df_mapeo = df_mapeo.dropna(subset=["Cuenta"]).drop_duplicates(subset=["Cuenta"], keep="first")
    return df_mapeo

@st.cache_data(show_spinner="Cargando hojas del balance...")
def cargar_balance(url, hojas):
    """Carga múltiples hojas desde el balance general"""
    r = requests.get(url)
    r.raise_for_status()
    file = BytesIO(r.content)
    data = {}
    for hoja in hojas:
        try:
            df = pd.read_excel(file, sheet_name=hoja, engine="openpyxl")
            df.columns = df.columns.str.strip()
            data[hoja] = df
        except Exception as e:
            st.warning(f"⚠️ No se pudo leer la hoja {hoja}: {e}")
    return data

@st.cache_data(show_spinner="Cargando hojas de info manual...")
def cargar_manual(url, hojas):
    """Carga múltiples hojas desde un archivo Excel remoto manteniendo estabilidad del puntero."""
    
    r = requests.get(url)
    r.raise_for_status()

    file = BytesIO(r.content)
    data = {}

    for hoja in hojas:
        try:
            file.seek(0)
            df = pd.read_excel(file, sheet_name=hoja, engine="openpyxl")
            df.columns = df.columns.str.strip()
            data[hoja] = df

        except Exception as e:
            st.warning(f"⚠️ No se pudo leer la hoja '{hoja}': {e}")

    return data


def limpiar_cuenta(x):
    """Limpia valores numéricos de la columna 'Cuenta'"""
    try:
        return int(str(x).strip().replace(".0", ""))
    except:
        return pd.NA

df_balance = load_data(balance_url)
df_mapeo = load_data(mapeo_url)
df_info = load_data(info_manual)

OPTIONS = [
    "BALANCE POR EMPRESA",
    "BALANCE GENERAL ACUMULADO",
    "BALANCE FINAL",
]

selected = option_menu(
    menu_title=None,
    options=OPTIONS,
    icons=["building", "bar-chart-line", "clipboard-data"],
    default_index=0,
    orientation="horizontal"
)

if selected == "BALANCE POR EMPRESA":

    def tabla_balance_por_empresa():
        st.subheader("Balance General por Empresa")

        df_mapeo_local = cargar_mapeo(mapeo_url)
        data_empresas = cargar_balance(balance_url, EMPRESAS)

        resultados = []
        balances_detallados = {}
        cuentas_no_mapeadas = []
        resumen_ingresos_egresos = []

        for empresa in EMPRESAS:
            if empresa not in data_empresas:
                continue
            df = data_empresas[empresa].copy()
            col_cuenta = next((c for c in COLUMNAS_CUENTA if c in df.columns), None)
            col_monto = next((c for c in COLUMNAS_MONTO if c in df.columns), None)
            if not col_cuenta or not col_monto:
                st.warning(f"⚠️ {empresa}: columnas inválidas ('Cuenta' / 'Saldo').")
                continue
            df[col_cuenta] = df[col_cuenta].apply(limpiar_cuenta)
            df[col_monto] = df[col_monto].replace("[\$,]", "", regex=True)
            df[col_monto] = pd.to_numeric(df[col_monto], errors="coerce").fillna(0)
            df = df.groupby(col_cuenta, as_index=False)[col_monto].sum()
            df_merged = df.merge(
                df_mapeo_local[["Cuenta", "CLASIFICACION", "CATEGORIA"]],
                on="Cuenta",
                how="left"
            )
            no_mapeadas = df_merged[df_merged["CLASIFICACION"].isna()].copy()

            if not no_mapeadas.empty:
                no_mapeadas["EMPRESA"] = empresa
                cuentas_no_mapeadas.append(no_mapeadas[["Cuenta", col_monto, "EMPRESA"]])
            df_merged = df_merged[~df_merged["CLASIFICACION"].isna()]

            if df_merged.empty:
                st.warning(f"⚠️ {empresa}: sin coincidencias exactas con el mapeo.")
                continue

            resumen = (
                df_merged.groupby(["CLASIFICACION", "CATEGORIA"])[col_monto]
                .sum().reset_index().rename(columns={col_monto: empresa})
            )

            resultados.append(resumen)
            balances_detallados[empresa] = df_merged.copy()

        if not resultados:
            st.error("❌ No se pudo generar información consolidada.")
            return

        data_resultados = []
        for empresa, df_emp in balances_detallados.items():
            if not {"CLASIFICACION", col_monto}.issubset(df_emp.columns):
                continue

            ingreso = df_emp.loc[df_emp["CLASIFICACION"] == "INGRESO", col_monto].sum()
            gasto = df_emp.loc[df_emp["CLASIFICACION"] == "GASTOS", col_monto].sum()
            utilidad = ingreso + gasto

            data_resultados.append({
                "EMPRESA": empresa,
                "INGRESO": ingreso,
                "GASTO": gasto,
                "UTILIDAD DEL EJE": utilidad
            })

        df_resultados = pd.DataFrame(data_resultados)

        st.markdown("Estado de Resultados por Empresa")

        df_resultados_t = (
            df_resultados
            .set_index("EMPRESA")
            .T
            .reset_index()
            .rename(columns={"index": "CONCEPTO"})
        )

        df_resultados_t["TOTAL"] = df_resultados_t[
            [c for c in df_resultados_t.columns if c != "CONCEPTO"]
        ].sum(axis=1)

        for col in df_resultados_t.columns:
            if col != "CONCEPTO":
                df_resultados_t[col] = df_resultados_t[col].apply(lambda x: f"${x:,.2f}")

        st.dataframe(
            df_resultados_t,
            use_container_width=True,
            hide_index=True
        )

        utilidad_total = df_resultados["UTILIDAD DEL EJE"].sum()
        st.session_state["UTILIDAD_EJE_TOTAL"] = utilidad_total

        st.markdown(f"💵 **Utilidad del eje consolidada:** ${utilidad_total:,.2f}")

        df_final = reduce(
            lambda l, r: pd.merge(l, r, on=["CLASIFICACION", "CATEGORIA"], how="outer"),
            resultados
        ).fillna(0)

        df_final["TOTAL ACUMULADO"] = df_final[EMPRESAS].sum(axis=1)
        st.session_state["df_final_empresa"] = df_final

        utilidades_por_empresa = {
            d["EMPRESA"]: d["UTILIDAD DEL EJE"] for d in data_resultados
        }

        total_capital_con_utilidad = 0.0

        for clasif in CLASIFICACIONES_PRINCIPALES:
            st.markdown(f"### 🔹 {clasif}")
            df_clasif = df_final[df_final["CLASIFICACION"] == clasif].copy()

            if df_clasif.empty:
                st.info(f"No hay cuentas clasificadas como {clasif}.")
                continue

            if clasif == "CAPITAL" and utilidades_por_empresa:
                fila_utilidad = pd.DataFrame({
                    "CLASIFICACION": [clasif],
                    "CATEGORIA": ["UTILIDAD DEL EJE"]
                })
                for empresa in EMPRESAS:
                    fila_utilidad[empresa] = utilidades_por_empresa.get(empresa, 0.0)

                fila_utilidad["TOTAL ACUMULADO"] = fila_utilidad[EMPRESAS].sum(axis=1)
                df_clasif = pd.concat([df_clasif, fila_utilidad], ignore_index=True)

            subtotal = pd.DataFrame({
                "CLASIFICACION": [clasif],
                "CATEGORIA": [f"TOTAL {clasif}"]
            })

            for col in EMPRESAS + ["TOTAL ACUMULADO"]:
                subtotal[col] = (
                    df_clasif[col].sum()
                    if pd.api.types.is_numeric_dtype(df_clasif[col])
                    else 0
                )

            df_clasif = pd.concat([df_clasif, subtotal], ignore_index=True)

            if clasif == "CAPITAL":
                total_capital_con_utilidad = float(subtotal["TOTAL ACUMULADO"].iloc[0])

            for col in EMPRESAS + ["TOTAL ACUMULADO"]:
                df_clasif[col] = df_clasif[col].apply(lambda x: f"${x:,.2f}")

            expanded_default = clasif == "CAPITAL"

            with st.expander(f"{clasif}", expanded=expanded_default):
                st.dataframe(
                    df_clasif.drop(columns=["CLASIFICACION"]),
                    use_container_width=True,
                    hide_index=True
                )

                if clasif == "CAPITAL":
                    st.markdown(
                        "💵 **Las utilidades del eje por empresa fueron integradas automáticamente al capital.**",
                        unsafe_allow_html=True
                    )

        totales = {
            c: df_final[df_final["CLASIFICACION"] == c]["TOTAL ACUMULADO"].sum()
            for c in CLASIFICACIONES_PRINCIPALES
        }

        if total_capital_con_utilidad != 0:
            totales["CAPITAL"] = total_capital_con_utilidad

        diferencia = totales["ACTIVO"] + (totales["PASIVO"] + totales["CAPITAL"])

        resumen_final = pd.DataFrame({
            "Concepto": ["TOTAL ACTIVO", "TOTAL PASIVO", "TOTAL CAPITAL", "DIFERENCIA"],
            "Monto Total": [
                f"${totales['ACTIVO']:,.2f}",
                f"${totales['PASIVO']:,.2f}",
                f"${totales['CAPITAL']:,.2f}",
                f"${diferencia:,.2f}"
            ]
        })

        st.markdown("### Resumen Consolidado")
        st.dataframe(resumen_final, use_container_width=True, hide_index=True)

        if abs(diferencia) < 1:
            st.success("✅ El balance está cuadrado (ACTIVO = PASIVO + CAPITAL).")
        else:
            st.error("❌ El balance no cuadra. Revisa las cuentas listadas.")

        # ✅ Mostrar SOLO si hay cuentas no mapeadas (SOLO NUMEROS DE CUENTA)
        if cuentas_no_mapeadas:
            st.markdown("## ⚠️ Cuentas NO mapeadas detectadas")
            df_no_mapeadas_total = pd.concat(cuentas_no_mapeadas)
            cuentas_unicas = sorted(df_no_mapeadas_total["Cuenta"].astype(str).unique().tolist())
            for _, row in df_no_mapeadas_total.iterrows():
                st.write(f"⚠️ {row['EMPRESA']} → {row['Cuenta']}")

        for empresa, df_emp in balances_detallados.items():
            if "Cuenta" in df_emp.columns and "Cuenta" in df_mapeo.columns:
                balances_detallados[empresa] = df_emp.merge(
                    df_mapeo[["Cuenta", "Descripción"]],
                    on="Cuenta",
                    how="left"
                )

        output = BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            for empresa, df_emp in balances_detallados.items():
                df_emp.to_excel(writer, index=False, sheet_name=empresa)

            df_final.to_excel(writer, index=False, sheet_name="Consolidado")
            resumen_final.to_excel(writer, index=False, sheet_name="Resumen")

        st.download_button(
            label="💾 Descargar Excel Consolidado",
            data=output.getvalue(),
            file_name="Balance_PorCuenta.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    tabla_balance_por_empresa()

elif selected == "BALANCE GENERAL ACUMULADO":
    st.markdown("### 🔄 Control manual de edición")
    if st.button("♻️ Recargar manuales"):
        st.session_state.pop("df_balance_manual", None)
        st.success("✅ Datos manuales recargados correctamente.")
        
    def tabla_inversiones(balance_url, mapeo_url):
        st.subheader("Inversiones entre Compañías")

        # ====== Cargar fuentes ======
        df_balance = cargar_balance(balance_url, EMPRESAS)   # dict: {hoja: df}
        df_mapeo = cargar_mapeo(mapeo_url)                  # df

        inversiones_dict = {
            "HDL-WH": {"hoja": "HOLDING", "Cuenta": "139000001"},
            "EHM-WH": {"hoja": "EHM", "Cuenta": "139000001"},
            "FWD-WH": {"hoja": "FWD", "Cuenta": "125000001"},
            "EHM-FWD": {"hoja": "EHM", "Cuenta": "139000003"},
            "EHM-UBIKARGA": {"hoja": "EHM", "Cuenta": "139000004"},
            "EHM-GREEN": {"hoja": "EHM", "Cuenta": "139000006"},
            "EHM-RESA": {"hoja": "EHM", "Cuenta": "139000007"},
            "EHM-HOLDING": {"hoja": "EHM", "Cuenta": "139000005"},
        }

        def _to_num_series(s):
            return (
                s.astype(str)
                .replace(r"[\$,]", "", regex=True)
                .pipe(pd.to_numeric, errors="coerce")
                .fillna(0.0)
            )

        def _detect_col(df, candidates):
            cols = {str(c).strip().lower(): c for c in df.columns}
            for cand in candidates:
                if cand.lower() in cols:
                    return cols[cand.lower()]
            return None

        def money_pos(v): return f"$ {v:,.2f}"
        def money_neg(v): return f"-$ {abs(v):,.2f}"

        def money_cell(v):
            if v is None:
                return "-"
            if isinstance(v, (int, float)):
                if abs(v) < 1e-12:
                    return "-"
                return money_neg(v) if v < 0 else money_pos(v)
            return str(v)

        col_map_cuenta = _detect_col(df_mapeo, ["Cuenta", "CUENTA", "codigo", "Código", "CODIGO", "CÓDIGO"])
        col_map_categoria = _detect_col(df_mapeo, ["CATEGORIA", "Categoría", "categoria"])
        if not col_map_cuenta or not col_map_categoria:
            st.error("❌ No pude detectar en el MAPEO las columnas 'Cuenta' y 'CATEGORIA'.")
            st.write("Columnas detectadas en mapeo:", df_mapeo.columns.tolist())
            return 0.0, 0.0, 0.0

        df_mapeo_local = df_mapeo.copy()
        df_mapeo_local[col_map_cuenta] = df_mapeo_local[col_map_cuenta].astype(str).str.strip()
        df_mapeo_local[col_map_categoria] = df_mapeo_local[col_map_categoria].astype(str).str.strip().str.upper()

        def cuentas_por_categoria(cat):
            return (
                df_mapeo_local.loc[df_mapeo_local[col_map_categoria] == str(cat).strip().upper(), col_map_cuenta]
                .dropna().astype(str).str.strip().unique().tolist()
            )

        cuentas_capital_social = cuentas_por_categoria("CAPITAL SOCIAL")
        cuentas_utilidades_acum = cuentas_por_categoria("UTILIDADES ACUMULADAS")

        if not cuentas_capital_social:
            st.error("❌ No encontré cuentas con CATEGORIA = 'CAPITAL SOCIAL' en tu mapeo.")
            return 0.0, 0.0, 0.0

        hojas_capital = ["WH", "FWD", "UBIKARGA", "GREEN", "RESA", "HOLDING"]

        def suma_saldo_final(hoja, cuentas):
            if hoja not in df_balance or not cuentas:
                return 0.0
            dfh = df_balance[hoja].copy()
            col_cuenta = _detect_col(dfh, ["Cuenta", "codigo", "Código", "CODIGO", "CÓDIGO"])
            col_saldo_final = next((c for c in dfh.columns if "saldo final" in str(c).lower()), None)
            if not col_cuenta or not col_saldo_final:
                return 0.0
            dfh[col_cuenta] = dfh[col_cuenta].astype(str).str.strip()
            dfh[col_saldo_final] = _to_num_series(dfh[col_saldo_final])
            return float(dfh.loc[dfh[col_cuenta].isin(cuentas), col_saldo_final].sum())

        capital_social_emp = {}
        for hoja in hojas_capital:
            cap = suma_saldo_final(hoja, cuentas_capital_social)
            capital_social_emp[hoja] = float(abs(cap))

        utilidades_acum_holding = float(abs(suma_saldo_final("HOLDING", cuentas_utilidades_acum)))
        montos_activo = {}
        for clave, info in inversiones_dict.items():
            hoja = info["hoja"]
            cuenta_objetivo = info["Cuenta"]

            if hoja not in df_balance:
                montos_activo[clave] = 0.0
                continue

            df = df_balance[hoja].copy()

            col_cuenta = _detect_col(df, ["Cuenta", "codigo", "Código", "CODIGO", "CÓDIGO"])
            col_monto = next((c for c in df.columns if "saldo final" in str(c).lower()), None)

            if not col_cuenta or not col_monto:
                montos_activo[clave] = 0.0
                continue

            df[col_cuenta] = df[col_cuenta].astype(str).str.strip()
            df[col_monto] = _to_num_series(df[col_monto])

            montos_activo[clave] = float(df.loc[df[col_cuenta] == str(cuenta_objetivo).strip(), col_monto].sum())

        AJUSTE_HLD_WH = 2_583_631.94
        if "HDL-WH" in montos_activo:
            montos_activo["HDL-WH"] = float(montos_activo["HDL-WH"] - AJUSTE_HLD_WH)

        b1_activos = [
            ("HLD-WH", montos_activo.get("HDL-WH", 0.0)),
            ("FWD-WH", montos_activo.get("FWD-WH", 0.0)),
            ("EHM-WH", montos_activo.get("EHM-WH", 0.0)),
        ]
        b1_total_activo = sum(v for _, v in b1_activos if isinstance(v, (int, float)))
        b1_total_social = capital_social_emp.get("WH", 0.0) 

        bloques = [
            ("EHM-FWD", montos_activo.get("EHM-FWD", 0.0), capital_social_emp.get("FWD", 0.0), "B2"),
            ("EHM-UBIKARGA", montos_activo.get("EHM-UBIKARGA", 0.0), capital_social_emp.get("UBIKARGA", 0.0), "B3"),
            ("EHM-GREEN", montos_activo.get("EHM-GREEN", 0.0), capital_social_emp.get("GREEN", 0.0), "B4"),
            ("EHM-RESA", montos_activo.get("EHM-RESA", 0.0), capital_social_emp.get("RESA", 0.0), "B5"),
            ("EHM-HOLDING", montos_activo.get("EHM-HOLDING", 0.0), capital_social_emp.get("HOLDING", 0.0), "B6")
        ]

        total_activo = float(sum(montos_activo.values()))
        total_social = float(b1_total_social + sum(b[2] for b in bloques)) 

        st.session_state["total_inversiones"] = total_activo
        st.session_state["total_social"] = total_social

        social_en_blanco_sum = 0.0

        for _, activo in b1_activos:
            if isinstance(activo, (int, float)):
                social_en_blanco_sum += abs(float(activo))

        for lbl, activo, _, _ in bloques:
            if lbl == "EHM-HOLDING":
                continue
            if isinstance(activo, (int, float)):
                social_en_blanco_sum += abs(float(activo))


        st.markdown(
            """
            <style>
            .inv-wrap { width: 100%; }
            table.inv {
                border-collapse: collapse;
                width: 100%;
                font-family: Arial, sans-serif;
                font-size: 13px;
            }
            table.inv td, table.inv th {
                border: 1px solid #d9d9d9;
                padding: 6px 8px;
                vertical-align: middle;
            }
            table.inv th {
                font-weight: 700;
                text-align: center;
                background: #ffffff;
            }
            td.lbl { text-align: left; width: 38%; }
            td.num { text-align: right; width: 20%; white-space: nowrap; }
            td.diff { text-align: right; width: 22%; white-space: nowrap; }
            tr.yellow td { background: #fff200; font-weight: 700; }
            tr.red td { background: #ff0000; font-weight: 700; color: #000000; }
            td.box { border: 2px solid #000000 !important; }
            .spacer { height: 14px; }
            </style>
            """,
            unsafe_allow_html=True
        )

        def render_header():
            return (
                "<tr>"
                "<th class='lbl'>INVERSIONES EN OTRAS COMPAÑÍAS</th>"
                "<th>ACTIVO</th>"
                "<th>SOCIAL</th>"
                "<th></th>"
                "</tr>"
            )

        def render_bloque(rows, total_activo_b, total_social_b, box_social_row_idx=None):
            """
            - SOCIAL en blanco -> social = -abs(activo) (visual)
            - AMARILLOS igual a tu cálculo actual, pero MOSTRANDO social en NEGATIVO
            """
            html = []
            html.append('<div class="inv-wrap"><table class="inv">')
            html.append(render_header())

            for i, r in enumerate(rows):
                lbl, activo = r

                social = None
                if social is None and isinstance(activo, (int, float)):
                    social = -abs(activo)

                diff = None

                social_cls = "num"
                if box_social_row_idx is not None and i == box_social_row_idx:
                    social_cls = "num box"

                html.append(
                    "<tr>"
                    f"<td class='lbl'>{lbl}</td>"
                    f"<td class='num'>{money_cell(activo)}</td>"
                    f"<td class='{social_cls}'>{money_cell(social)}</td>"
                    f"<td class='diff'>{money_cell(diff)}</td>"
                    "</tr>"
                )

            social_yellow = -abs(total_social_b or 0.0)
            tdiff = (total_activo_b or 0.0) + social_yellow

            html.append(
                "<tr class='yellow'>"
                "<td class='lbl'>TOTAL CAPITAL SOCIAL</td>"
                f"<td class='num'>{money_cell(total_activo_b)}</td>"
                f"<td class='num'>{money_cell(social_yellow)}</td>"
                f"<td class='diff'>{money_cell(tdiff)}</td>"
                "</tr>"
            )

            html.append("</table></div>")
            return "\n".join(html)

        st.markdown(render_bloque(b1_activos, b1_total_activo, b1_total_social), unsafe_allow_html=True)
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

        goodwill = 0.0  

        for lbl, activo, social_total, tag in bloques:
            if lbl != "EHM-HOLDING":
                rows = [(lbl, activo)]
                box_idx = 0 if lbl == "EHM-RESA" else None
                st.markdown(render_bloque(rows, activo, social_total, box_social_row_idx=box_idx), unsafe_allow_html=True)
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
                continue

            social_holding_visual = -abs(capital_social_emp.get("HOLDING", 0.0))
            util_holding_visual = -abs(utilidades_acum_holding)

            total_activo_ultimo = float(activo)
            total_social_ultimo = float(social_holding_visual + util_holding_visual)
            total_diff_ultimo = total_activo_ultimo + total_social_ultimo

            goodwill = abs(float(total_diff_ultimo))
            st.session_state["GOODWILL"] = goodwill

            html_last = []
            html_last.append('<div class="inv-wrap"><table class="inv">')
            html_last.append(render_header())

            html_last.append(
                "<tr>"
                f"<td class='lbl'>{lbl}</td>"
                f"<td class='num'>{money_cell(activo)}</td>"
                f"<td class='num'>{money_cell(social_holding_visual)}</td>"
                f"<td class='diff'>-</td>"
                "</tr>"
            )

            html_last.append(
                "<tr>"
                "<td class='lbl'>UTILIDADES ACUM METODO DE PARTICIPACION</td>"
                f"<td class='num'>-</td>"
                f"<td class='num'>{money_cell(util_holding_visual)}</td>"
                f"<td class='diff'>-</td>"
                "</tr>"
            )

            html_last.append(
                "<tr class='red'>"
                "<td class='lbl'>TOTAL</td>"
                f"<td class='num'>{money_cell(total_activo_ultimo)}</td>"
                f"<td class='num'>{money_cell(total_social_ultimo)}</td>"
                f"<td class='diff'>{money_cell(total_diff_ultimo)}</td>"
                "</tr>"
            )

            social_yellow = -abs(social_total or 0.0)
            tdiff = (activo or 0.0) + social_yellow
            html_last.append(
                "<tr class='yellow'>"
                "<td class='lbl'>TOTAL CAPITAL SOCIAL</td>"
                f"<td class='num'>{money_cell(activo)}</td>"
                f"<td class='num'>{money_cell(social_yellow)}</td>"
                f"<td class='diff'>{money_cell(tdiff)}</td>"
                "</tr>"
            )

            html_last.append("</table></div>")
            st.markdown("\n".join(html_last), unsafe_allow_html=True)
            st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

        st.subheader("Consolidación Inversiones en Acciones")

        debe_capital_social = float(social_en_blanco_sum)

        df_consol = pd.DataFrame({
            "CONCEPTO": ["INVERSIONES EN ACCIONES", "CAPITAL SOCIAL", "GOODWILL", "TOTAL"],
            "DEBE": [0.0, debe_capital_social, goodwill, (0.0 + debe_capital_social + goodwill)],
            "HABER": [total_activo, 0.0, 0.0, total_activo],
        })

        st.dataframe(
            df_consol.style.format({"DEBE": "${:,.2f}", "HABER": "${:,.2f}"}),
            use_container_width=True,
            hide_index=True
        )

        return total_activo, total_social, goodwill

    def tabla_ingresos_egresos(balance_url, info_manual):
        st.subheader("Ingresos y Gastos del Ejercicio")

        data_empresas = cargar_balance(balance_url, EMPRESAS)
        data_manual = cargar_manual(info_manual, ["INTEREMPRESAS"])
        df_inter = data_manual.get("INTEREMPRESAS")

        if df_inter is None:
            st.error("❌ No se encontró la hoja 'INTEREMPRESAS' en info_manual.")
            return None, None
        df_inter.columns = df_inter.columns.str.strip().str.upper()
        try:
            debe_inter = float(
                df_inter.loc[df_inter["INTEREMPRESA"] == "INGRESO", "TOTALES"].iloc[0]
            )
        except Exception:
            debe_inter = 0.0

        try:
            haber_inter = float(
                df_inter.loc[df_inter["INTEREMPRESA"] == "GASTO", "TOTALES"].iloc[0]
            )
        except Exception:
            haber_inter = 0.0

        resultados = []
        for hoja in EMPRESAS:
            if hoja not in data_empresas:
                continue
            df = data_empresas[hoja].copy()
            col_cuenta = next((c for c in df.columns if "CUENTA" in str(c).upper()), None)
            col_monto = next((c for c in COLUMNAS_MONTO if c in df.columns), None)
            if not col_cuenta or not col_monto:
                continue

            df[col_cuenta] = pd.to_numeric(df[col_cuenta], errors="coerce")
            df[col_monto] = (
                df[col_monto]
                .replace("[\$,]", "", regex=True)
                .pipe(pd.to_numeric, errors="coerce")
                .fillna(0)
            )
            df["CLASIFICACION"] = df[col_cuenta].apply(
                lambda x: "INGRESO" if 400_000_000 <= x < 500_000_000
                else ("GASTO" if 500_000_000 <= x < 600_000_000 else None)
            )
            df_filtrado = df[df["CLASIFICACION"].notna()]

            resumen = (
                df_filtrado.groupby("CLASIFICACION")[col_monto]
                .sum()
                .reset_index()
            )
            ingreso = resumen.loc[resumen["CLASIFICACION"] == "INGRESO", col_monto].sum()
            gasto = resumen.loc[resumen["CLASIFICACION"] == "GASTO", col_monto].sum()

            resultados.append({
                "EMPRESA": hoja,
                "INGRESOS": ingreso,
                "GASTOS": gasto
            })

        df_final = pd.DataFrame(resultados)
        ingreso_total = df_final["INGRESOS"].sum()
        gasto_total = df_final["GASTOS"].sum()
        utilidad_total = ingreso_total + gasto_total

        df_resultado = pd.DataFrame({
            "CLASIFICACIÓN": ["INGRESO", "GASTO", "UTILIDAD DEL EJE"],
            "RESULTADO": [ingreso_total, gasto_total, utilidad_total],
            "DEBE": [debe_inter, 0.0, 0.0],
            "HABER": [0.0, haber_inter, 0.0],
        })

        df_resultado["TOTALES"] = (
            df_resultado["RESULTADO"] + df_resultado["DEBE"] - df_resultado["HABER"]
        )

        st.dataframe(
            df_resultado.style.format({
                "RESULTADO": "${:,.2f}",
                "DEBE": "${:,.2f}",
                "HABER": "${:,.2f}",
                "TOTALES": "${:,.2f}",
            }),
            use_container_width=True,
            hide_index=True
        )

        st.session_state["UTILIDAD_EJE_TOTAL"] = utilidad_total

        return df_resultado, df_final

    def tabla_ingresos_gastos2(df_resultado, info_manual):

        st.subheader("Tabla de Ingresos")
        data_manual = cargar_manual(info_manual, ["Hoja 3"])
        df_manual = data_manual.get("Hoja 3")

        if df_manual is None:
            st.error("❌ No se encontró la hoja 'Hoja 3' en info_manual.")
            return None

        df_manual.columns = df_manual.columns.str.strip().str.upper()
        try:
            ingresos_reales = float(
                df_manual.loc[df_manual["CONCEPTO"] == "INGRESOS REALES", "VALOR"].iloc[0]
            )
        except Exception:
            ingresos_reales = 0.0

        ingresos_facturados_resultado = df_resultado.loc[
            df_resultado["CLASIFICACIÓN"] == "INGRESO", "TOTALES"
        ].iloc[0]*-1
        total_p_facturados = ingresos_reales - ingresos_facturados_resultado
        iva_por_pagar = total_p_facturados * 0.16
        total_p_facturar = total_p_facturados + iva_por_pagar

        df_resumen = pd.DataFrame({
            "CONCEPTO": [
                "INGRESOS REALES",
                "INGRESOS FACTURADOS",
                "TOTAL PENDIENTE POR FACTURAR",
                "IVA POR PAGAR",
                "TOTAL POR FACTURAR"
            ],
            "VALOR": [
                ingresos_reales,
                ingresos_facturados_resultado,
                total_p_facturados,
                iva_por_pagar,
                total_p_facturar
            ]
        })

        st.dataframe(
            df_resumen.style.format({"VALOR": "${:,.2f}"}),
            use_container_width=True,
            hide_index=True
        )

        return total_p_facturados, iva_por_pagar, total_p_facturar

    def tabla_gastos2(df_resultado, info_manual):

        st.subheader("Tabla de Gastos")

        data_manual = cargar_manual(info_manual, ["Hoja 3"])
        df_manual = data_manual.get("Hoja 3")
        if df_manual is None:
            st.error("❌ No se encontró la hoja 'Hoja 3' en info_manual.")
            return None

        df_manual.columns = df_manual.columns.str.strip().str.upper()

        def extraer_valor(nombre):
            try:
                return float(df_manual.loc[df_manual["CONCEPTO"] == nombre, "VALOR"].iloc[0])
            except Exception:
                return 0.0

        gastos_reales = extraer_valor("GASTOS REALES")
        impuestos = extraer_valor("IMPUESTOS")
        reconocimiento_impuestos = extraer_valor("RECONOCIMIENTO DE IMPUESTOS")

        gastos_facturados = df_resultado.loc[
            df_resultado["CLASIFICACIÓN"] == "GASTO", "TOTALES"
        ].iloc[0]

        provision_gastos = gastos_reales - gastos_facturados + impuestos
        total_g_facturados = provision_gastos - reconocimiento_impuestos
        iva_p_acreditar = total_g_facturados* 0.16
        total_g_por_facturar = total_g_facturados + iva_p_acreditar

        df_resumen = pd.DataFrame({
            "CONCEPTO": [
                "GASTOS REALES",
                "IMPUESTOS",
                "GASTOS FACTURADOS",
                "RECONOCIMIENTO DE IMPUESTOS",
                "PROVISIÓN DE GASTOS",
                "TOTAL GASTOS FACTURADOS",
                "IVA POR ACREDITAR",
                "TOTAL GASTOS POR FACTURAR"
            ],
            "VALOR": [
                gastos_reales,
                impuestos,
                gastos_facturados,
                reconocimiento_impuestos,
                provision_gastos,
                total_g_facturados,
                iva_p_acreditar,
                total_g_por_facturar
            ]
        })

        st.dataframe(
            df_resumen.style.format({"VALOR": "${:,.2f}"}),
            use_container_width=True,
            hide_index=True
        )

        return provision_gastos, iva_p_acreditar, total_g_por_facturar, reconocimiento_impuestos

    def tabla_ingresos_egresos2(total_p_facturados, df_resultado, provision_gastos):

        st.subheader("Ingresos y Gastos del Ejercicio")
        try:
            ingreso_total_t = df_resultado.loc[
                df_resultado["CLASIFICACIÓN"] == "INGRESO", "TOTALES"
            ].iloc[0]
        except:
            ingreso_total_t = 0.0

        try:
            gasto_total_t = df_resultado.loc[
                df_resultado["CLASIFICACIÓN"] == "GASTO", "TOTALES"
            ].iloc[0]
        except:
            gasto_total_t = 0.0

        utilidad_total_real = ingreso_total_t + gasto_total_t
        ingreso_resultado = ingreso_total_t
        gasto_resultado   = gasto_total_t
        utilidad_resultado = utilidad_total_real

        df_out = pd.DataFrame({
            "CLASIFICACIÓN": ["INGRESO", "GASTO", "UTILIDAD DEL EJE"],
            "RESULTADO": [ingreso_resultado, gasto_resultado, utilidad_resultado],
            "DEBE": [0.0, provision_gastos, provision_gastos],
            "HABER": [total_p_facturados, 0.0, total_p_facturados]
        })
        df_out["TOTALES"] = df_out["RESULTADO"] + df_out["DEBE"] - df_out["HABER"]

        st.session_state["df_ingresos_egresos2"] = df_out.copy()
        st.session_state["UTILIDAD_EJE_TOTAL"] = utilidad_total_real + df_out["DEBE"].sum() - df_out["HABER"].sum()

        st.dataframe(
            df_out.style.format({
                "RESULTADO": "${:,.2f}",
                "DEBE": "${:,.2f}",
                "HABER": "${:,.2f}",
                "TOTALES": "${:,.2f}",
            }),
            use_container_width=True,
            hide_index=True
        )

        return df_out

    def tabla_balance_acumulado(total_activo, total_social, goodwill, balance_url, mapeo_url, UTILIDAD_EJE_TOTAL, total_p_facturar, iva_p_acreditar, iva_p_pagar, info_manual, total_g_por_facturar, reconocimiento_impuestos):

        st.subheader("Balance General Acumulado")
        df_mapeo_local = cargar_mapeo(mapeo_url)
        data_empresas = cargar_balance(balance_url, EMPRESAS)

        resultados = []
        balances_detallados = {}
        cuentas_no_mapeadas = []

        for empresa in EMPRESAS:
            if empresa not in data_empresas:
                continue

            df = data_empresas[empresa].copy()
            col_cuenta = next((c for c in COLUMNAS_CUENTA if c in df.columns), None)
            col_monto = next((c for c in COLUMNAS_MONTO if c in df.columns), None)

            if not col_cuenta or not col_monto:
                st.warning(f"⚠️ {empresa}: columnas inválidas ('Cuenta' / 'Saldo').")
                continue

            df[col_cuenta] = df[col_cuenta].apply(limpiar_cuenta)
            df[col_monto] = df[col_monto].replace("[\$,]", "", regex=True)
            df[col_monto] = pd.to_numeric(df[col_monto], errors="coerce").fillna(0)
            df = df.groupby(col_cuenta, as_index=False)[col_monto].sum()

            df_merged = df.merge(
                df_mapeo_local[["Cuenta", "CLASIFICACION", "CATEGORIA"]],
                left_on=col_cuenta,
                right_on="Cuenta",
                how="left"
            )

            no_mapeadas = df_merged[df_merged["CLASIFICACION"].isna()].copy()
            if not no_mapeadas.empty:
                no_mapeadas["EMPRESA"] = empresa
                cuentas_no_mapeadas.append(no_mapeadas[["Cuenta", col_monto, "EMPRESA"]])

            df_merged = df_merged[~df_merged["CLASIFICACION"].isna()]
            if df_merged.empty:
                st.warning(f"⚠️ {empresa}: sin coincidencias exactas con el mapeo.")
                continue

            resumen = (
                df_merged.groupby(["CLASIFICACION", "CATEGORIA"])[col_monto]
                .sum()
                .reset_index()
                .rename(columns={col_monto: empresa})
            )

            resultados.append(resumen)
            balances_detallados[empresa] = df_merged.copy()

        if not resultados:
            st.error("❌ No se generó información para consolidación.")
            return None

        data_manual = cargar_manual(info_manual, ["CXP"])
        df_cxp = data_manual.get("CXP")

        monto_cxp_cr = 0.0 

        if df_cxp is not None and not df_cxp.empty:
            df_cxp = df_cxp.copy()
            df_cxp.columns = df_cxp.columns.astype(str).str.strip()
            col_etiqueta = next((c for c in df_cxp.columns if "Etiquetas de fila" in c), None)
            col_cr = next((c for c in df_cxp.columns if "Suma de ACCOUNTED_CR" in c), None)

            if col_cr is None:
                st.warning("⚠️ No se encontró la columna 'Suma de ACCOUNTED_CR' en la hoja CXP.")
            else:
                # Normaliza a número
                df_cxp[col_cr] = (
                    df_cxp[col_cr].astype(str)
                    .str.replace(r"[\$,]", "", regex=True)
                )
                df_cxp[col_cr] = pd.to_numeric(df_cxp[col_cr], errors="coerce").fillna(0)
                if col_etiqueta:
                    et = df_cxp[col_etiqueta].astype(str).str.upper().str.strip()
                    mask_cxp = et.str.contains("CXP") | et.str.contains("PROVEED")
                    monto_cxp_cr = float(df_cxp.loc[mask_cxp, col_cr].sum())
                    if monto_cxp_cr == 0:
                        monto_cxp_cr = float(df_cxp[col_cr].sum())
                else:
                    monto_cxp_cr = float(df_cxp[col_cr].sum())
        else:
            st.warning("⚠️ No se encontró o viene vacía la hoja 'CXP' en info_manual.")


        df_total = reduce(
            lambda l, r: pd.merge(l, r, on=["CLASIFICACION", "CATEGORIA"], how="outer"),
            resultados
        ).fillna(0)

        cols_empresas = [
            c for c in df_total.columns
            if c not in ["CLASIFICACION", "CATEGORIA", "ACUMULADO", "DEBE", "HABER", "MANUAL", "TOTALES"]
        ]

        df_total["ACUMULADO"] = df_total[cols_empresas].sum(axis=1)
        df_total["DEBE"] = 0.0
        df_total["HABER"] = 0.0
        df_total["MANUAL"] = 0.0

        df_total.loc[
            df_total["CATEGORIA"].str.contains("DEUDORES RELACIONADOS", case=False),
            "HABER"
        ] = df_total["ACUMULADO"]

        imp_dif_activo = df_total.loc[
            (df_total["CLASIFICACION"] == "ACTIVO") &
            (df_total["CATEGORIA"].str.contains("IMPUESTOS DIFERIDOS", case=False)),
            "ACUMULADO"
        ].sum()

        df_total.loc[
            (df_total["CLASIFICACION"] == "PASIVO") &
            (df_total["CATEGORIA"].str.contains("IMPUESTOS DIFERIDOS", case=False)),
            "DEBE"
        ] = imp_dif_activo

        df_total.loc[
            (df_total["CLASIFICACION"] == "PASIVO") &
            (df_total["CATEGORIA"].str.contains("ISR", case=False)),
            "HABER"
        ] = df_total["ACUMULADO"]

        df_total.loc[
            (df_total["CLASIFICACION"] == "PASIVO") &
            (df_total["CATEGORIA"].str.contains("Anticipos de ISR", case=False)),
            "DEBE"
        ] = df_total["ACUMULADO"]

        acreedores_relacionados = df_total.loc[
            (df_total["CLASIFICACION"] == "PASIVO") &
            (df_total["CATEGORIA"].str.contains("ACREEDORES RELACIONADOS", case=False)),
            "ACUMULADO"
        ].sum()
        deudores_relacionados = df_total.loc[
            (df_total["CLASIFICACION"] == "ACTIVO") &
            (df_total["CATEGORIA"].str.contains("DEUDORES RELACIONADOS", case=False)),
            "ACUMULADO"
        ].sum()
        df_total.loc[
            (df_total["CLASIFICACION"] == "PASIVO") &
            (df_total["CATEGORIA"].str.contains("ACREEDORES DIVERSOS", case=False)),
            "HABER"
        ] = acreedores_relacionados + deudores_relacionados
        df_total.loc[
            (df_total["CLASIFICACION"] == "PASIVO") &
            (df_total["CATEGORIA"].str.contains("ACREEDORES DIVERSOS", case=False)),
            "DEBE"
        ] = acreedores_relacionados + deudores_relacionados
        df_total.loc[
            (df_total["CLASIFICACION"] == "PASIVO") &
            (df_total["CATEGORIA"].str.contains("ACREEDORES RELACIONADOS", case=False)),
            "DEBE"
        ] = acreedores_relacionados*-1

        df_total.loc[
            df_total["CATEGORIA"].str.contains("IVA POR TRASLADAR", case=False),
            "HABER"
        ] = iva_p_pagar

        total_capital_social = total_social*-1
        df_total.loc[
            df_total["CATEGORIA"].str.contains("CAPITAL SOCIAL", case=False),
            "DEBE"
        ] = total_capital_social

        df_total.loc[
            (df_total["CLASIFICACION"] == "PASIVO") &
            (df_total["CATEGORIA"].str.contains("ISR", case=False)),
            "ACUMULADO"
        ].sum()

        servicios_cobrados_adelantado=df_total.loc[
            (df_total["CLASIFICACION"] == "PASIVO") &
            (df_total["CATEGORIA"].str.contains("SERVICIOS COBRADOS POR ADELANTADO", case=False)),
            "ACUMULADO"
        ].sum()

        df_total.loc[
            (df_total["CLASIFICACION"] == "ACTIVO") &
            (df_total["CATEGORIA"].str.contains("SERVICIOS PAGADOS POR ADELANTADO", case=False)),
            "DEBE"
        ] = servicios_cobrados_adelantado

        df_total.loc[
            (df_total["CLASIFICACION"] == "PASIVO") &
            (df_total["CATEGORIA"].str.contains("SERVICIOS COBRADOS POR ADELANTADO", case=False)),
            "HABER"
        ] = servicios_cobrados_adelantado

        ajuste_iva_acreditable = monto_cxp_cr * 0.16

        df_total.loc[
            df_total["CATEGORIA"].str.contains("IVA ACREDITABLE", case=False),
            "ACUMULADO"
        ] = (
            df_total.loc[
                df_total["CATEGORIA"].str.contains("IVA ACREDITABLE", case=False),
                "ACUMULADO"
            ] - ajuste_iva_acreditable
        )
        df_total.loc[
            (df_total["CLASIFICACION"] == "ACTIVO") &
            (df_total["CATEGORIA"].str.contains("IVA ACREDITABLE", case=False)),
            "HABER"
        ] = ajuste_iva_acreditable

        df_total.loc[
            (df_total["CLASIFICACION"] == "PASIVO") &
            (df_total["CATEGORIA"].str.contains("IVA POR TRASLADAR", case=False)),
            "DEBE"
        ] = ajuste_iva_acreditable

        df_total["TOTALES"] = df_total["ACUMULADO"] + df_total["DEBE"] - df_total["HABER"]

        if "df_balance_manual" not in st.session_state:
            st.session_state["df_balance_manual"] = df_total.copy()
 
        df_total.loc[
            (df_total["CLASIFICACION"] == "PASIVO") &
            (df_total["CATEGORIA"].str.contains("PROVEEDORES", case=False)),
            "DEBE"
        ] += monto_cxp_cr

        df_total.loc[
            (df_total["CLASIFICACION"] == "ACTIVO") &
            (df_total["CATEGORIA"].str.contains("CUENTAS POR COBRAR", case=False)),
            "HABER"
        ] += monto_cxp_cr

        df_editado = st.data_editor(
            st.session_state["df_balance_manual"],
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            column_config={
                "MANUAL": st.column_config.NumberColumn("Manual (editable)", format="%.2f")
            },
            key="balance_acumulado_editor",
        )

        df_editado["TOTALES"] = (
            df_editado["ACUMULADO"] +
            df_editado["DEBE"] -
            df_editado["HABER"] +
            df_editado["MANUAL"]
        )

        st.session_state["df_balance_manual"] = df_editado

        util_eje = UTILIDAD_EJE_TOTAL
        total_capital_con_utilidad = 0.0

        for clasif in CLASIFICACIONES_PRINCIPALES:

            df_clasif = df_editado[df_editado["CLASIFICACION"] == clasif].copy()
            df_clasif["Descripción"] = df_clasif.apply(
                lambda row: row.get("Descripción", row["CATEGORIA"]),
                axis=1
            )

            if clasif == "ACTIVO":

                fila_goodwill = pd.DataFrame({
                    "CLASIFICACION": ["ACTIVO"],
                    "Descripción": ["GOODWILL"],
                    "ACUMULADO": [0.0],
                    "DEBE": [goodwill],
                    "HABER": [0.0],
                    "MANUAL": [0.0],
                    "TOTALES": [goodwill]
                })

                fila_no_fact = pd.DataFrame({
                    "CLASIFICACION": ["ACTIVO"],
                    "Descripción": ["CUENTAS POR COBRAR NO FACTURADAS"],
                    "ACUMULADO": [0.0],
                    "DEBE": [total_p_facturar],
                    "HABER": [0.0],
                    "MANUAL": [0.0],
                    "TOTALES": [total_p_facturar]
                })

                df_clasif = pd.concat([df_clasif, fila_goodwill, fila_no_fact], ignore_index=True)

            if clasif == "PASIVO":

                fila_fletes = pd.DataFrame({
                    "CLASIFICACION": ["PASIVO"],
                    "Descripción": ["FLETES NO FACTURADOS"],
                    "ACUMULADO": [0.0],
                    "DEBE": [0.0],
                    "HABER": [total_g_por_facturar],
                    "MANUAL": [0.0],
                    "TOTALES": [0.0 + 0.0 - total_g_por_facturar]
                })

                df_clasif = pd.concat([df_clasif, fila_fletes], ignore_index=True)

            if clasif == "CAPITAL":

                fila_utilidad = pd.DataFrame({
                    "CLASIFICACION": ["CAPITAL"],
                    "Descripción": ["UTILIDAD DEL EJE"],
                    "ACUMULADO": [util_eje],
                    "DEBE": [0.0],
                    "HABER": [0.0],
                    "MANUAL": [0.0],
                    "TOTALES": [util_eje]
                })

                df_clasif = pd.concat([df_clasif, fila_utilidad], ignore_index=True)

            subtotal = pd.DataFrame({
                "CLASIFICACION": [clasif],
                "Descripción": [f"TOTAL {clasif}"],
                "ACUMULADO": [df_clasif["ACUMULADO"].sum()],
                "DEBE": [df_clasif["DEBE"].sum()],
                "HABER": [df_clasif["HABER"].sum()],
                "MANUAL": [df_clasif["MANUAL"].sum()],
                "TOTALES": [df_clasif["TOTALES"].sum()]
            })

            df_clasif = pd.concat([df_clasif, subtotal], ignore_index=True)

            if clasif == "CAPITAL":
                total_capital_con_utilidad = float(subtotal["TOTALES"].iloc[0])

            with st.expander(f"{clasif}", expanded=(clasif == "CAPITAL")):
                st.dataframe(
                    df_clasif[["Descripción", "ACUMULADO", "DEBE", "HABER", "TOTALES"]]
                    .style.format({
                        "ACUMULADO": "${:,.2f}",
                        "DEBE": "${:,.2f}",
                        "HABER": "${:,.2f}",
                        "TOTALES": "${:,.2f}",
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        totales = {
            c: df_editado[df_editado["CLASIFICACION"] == c]["TOTALES"].sum()
            for c in CLASIFICACIONES_PRINCIPALES
        }
        totales["ACTIVO"] += goodwill + total_p_facturar
        totales["PASIVO"] += (total_g_por_facturar*-1)

        if total_capital_con_utilidad != 0:
            totales["CAPITAL"] = total_capital_con_utilidad

        diferencia = totales["ACTIVO"] + (totales["PASIVO"] + totales["CAPITAL"])

        resumen_final = pd.DataFrame({
            "Concepto": ["TOTAL ACTIVO", "TOTAL PASIVO", "TOTAL CAPITAL", "DIFERENCIA"],
            "Monto Total": [
                f"${totales['ACTIVO']:,.2f}",
                f"${totales['PASIVO']:,.2f}",
                f"${totales['CAPITAL']:,.2f}",
                f"${diferencia:,.2f}"
            ]
        })

        st.markdown("### Resumen Consolidado")
        st.dataframe(resumen_final, use_container_width=True, hide_index=True)
        
        st.session_state["goodwill"] = goodwill
        st.session_state["total_p_facturar"] = total_p_facturar
        st.session_state["total_g_por_facturar"] = total_g_por_facturar
        st.session_state["UTILIDAD_EJE_TOTAL"] = UTILIDAD_EJE_TOTAL
        
        return df_editado

    total_activo, total_social, goodwill = tabla_inversiones(balance_url, mapeo_url)
    df_resultado, df_final = tabla_ingresos_egresos(balance_url, info_manual)
    total_p_facturados, iva_p_pagar, total_p_facturar = tabla_ingresos_gastos2(df_resultado, info_manual)
    provision_gastos, iva_p_acreditar, total_g_por_facturar, reconocimiento_impuestos = tabla_gastos2(df_resultado, info_manual)
    df_ing_egr2 = tabla_ingresos_egresos2(total_p_facturados, df_resultado, provision_gastos)
    tabla_balance_acumulado(total_activo, total_social, goodwill, balance_url, mapeo_url, st.session_state["UTILIDAD_EJE_TOTAL"], total_p_facturar, iva_p_acreditar, iva_p_pagar,info_manual, total_g_por_facturar, reconocimiento_impuestos)

elif selected == "BALANCE FINAL":
    def tabla_BALANCE_FINAL(df_editado, goodwill, total_p_facturar, UTILIDAD_EJE_TOTAL, total_g_por_facturar):
        st.subheader("📘 BALANCE FINAL (Después de Ajustes Debe/Haber)")

        if df_editado is None or df_editado.empty:
            st.warning("⚠️ No hay información para mostrar el Balance Final")
            return
        
        columnas = ["CLASIFICACION", "CATEGORIA", "TOTALES"]
        df_balance = df_editado[columnas].copy()

        totales_dict = {}

        for clasif in ["ACTIVO", "PASIVO", "CAPITAL"]:
            df_clasif = df_balance[df_balance["CLASIFICACION"] == clasif].copy()

            if df_clasif.empty:
                continue

            # --- Total base por clasificación ---
            base_total = df_clasif["TOTALES"].sum()

            # --- Ajustes adicionales por clasificación ---
            extra = 0.0
            if clasif == "ACTIVO":
                extra = float(goodwill or 0) + float(total_p_facturar or 0)
            elif clasif == "PASIVO":
                extra = float(total_g_por_facturar or 0)
            elif clasif == "CAPITAL":
                extra = float(UTILIDAD_EJE_TOTAL or 0)

            total_valor = base_total + extra
            totales_dict[clasif] = total_valor  

            # --- Lo que se muestra en pantalla (misma lógica que tu código original) ---
            df_show = df_clasif[["CATEGORIA", "TOTALES"]].copy()

            if clasif == "ACTIVO":
                df_show.loc[len(df_show)] = ["GOODWILL", goodwill]
                df_show.loc[len(df_show)] = ["CxC NO FACTURADAS", total_p_facturar]

            if clasif == "PASIVO":
                df_show.loc[len(df_show)] = ["FLETES NO FACTURADOS", total_g_por_facturar]

            if clasif == "CAPITAL":
                df_show.loc[len(df_show)] = ["UTILIDAD DEL EJE", UTILIDAD_EJE_TOTAL]

            total_row = pd.DataFrame({
                "CATEGORIA": [f"TOTAL {clasif}"],
                "TOTALES": [totales_dict[clasif]]
            })

            df_show = pd.concat([df_show, total_row], ignore_index=True)

            with st.expander(f"{clasif}", expanded=True if clasif == "ACTIVO" else False):
                st.dataframe(
                    df_show.style.format({"TOTALES": "${:,.2f}"}),
                    use_container_width=True,
                    hide_index=True
                )

        # --- Resumen general ---
        total_activo = totales_dict.get("ACTIVO", 0)
        total_pasivo = totales_dict.get("PASIVO", 0)
        total_capital = totales_dict.get("CAPITAL", 0)
        diferencia = total_activo - (total_pasivo + total_capital)

        resumen_final = pd.DataFrame({
            "Concepto": ["TOTAL ACTIVO", "TOTAL PASIVO", "TOTAL CAPITAL", "DIFERENCIA"],
            "MONTO": [total_activo, total_pasivo, total_capital, diferencia]
        })

        st.markdown("### 📊 Resumen Final")
        st.dataframe(resumen_final.style.format({"MONTO": "${:,.2f}"}),
                    use_container_width=True, hide_index=True)

        # --- Exportar a Excel (misma lógica que tenías, usando los totales ajustados) ---
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

            for clasif in ["ACTIVO", "PASIVO", "CAPITAL"]:
                df_export = df_balance[df_balance["CLASIFICACION"] == clasif][["CATEGORIA", "TOTALES"]].copy()

                if clasif == "ACTIVO":
                    df_export.loc[len(df_export)] = ["GOODWILL", goodwill]
                    df_export.loc[len(df_export)] = ["CxC NO FACTURADAS", total_p_facturar]

                if clasif == "PASIVO":
                    df_export.loc[len(df_export)] = ["FLETES NO FACTURADOS", total_g_por_facturar]

                if clasif == "CAPITAL":
                    df_export.loc[len(df_export)] = ["UTILIDAD DEL EJE", UTILIDAD_EJE_TOTAL]

                df_export.loc[len(df_export)] = [f"TOTAL {clasif}", totales_dict[clasif]]
                df_export.to_excel(writer, index=False, sheet_name=clasif)

            resumen_export = pd.DataFrame({
                "Concepto": ["TOTAL ACTIVO", "TOTAL PASIVO", "TOTAL CAPITAL", "DIFERENCIA"],
                "Monto": [total_activo, total_pasivo, total_capital, diferencia]
            })

            resumen_export.to_excel(writer, index=False, sheet_name="Resumen Final")
            workbook = writer.book
            for sheet_name in writer.sheets.keys():
                worksheet = writer.sheets[sheet_name]
                money_format = workbook.add_format({'num_format': '$#,##0.00', 'align': 'right'})
                header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1})
                worksheet.set_row(0, None, header_format)
                worksheet.set_column("A:A", 40)
                worksheet.set_column("B:B", 25, money_format)
                worksheet.freeze_panes(1, 0)
                worksheet.fit_to_pages(1, 0)

        st.download_button(
            label="💾 Descargar Balance Final",
            data=output.getvalue(),
            file_name="Balance_Final_ESGARI.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


    # Llamada (igual que ya la tenías)
    if "df_balance_manual" in st.session_state:
        goodwill = st.session_state.get("goodwill", 0)
        total_p_facturar = st.session_state.get("total_p_facturar", 0)
        util_eje = st.session_state.get("UTILIDAD_EJE_TOTAL", 0)
        total_g_por_facturar = st.session_state.get("total_g_por_facturar", 0)

        tabla_BALANCE_FINAL(
            st.session_state["df_balance_manual"],
            goodwill,
            total_p_facturar,
            util_eje,
            total_g_por_facturar
        )
    else:
        st.warning("⚠️ Ejecuta primero el Balance Acumulado")



   

























































































