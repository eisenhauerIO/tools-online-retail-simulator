def has_synthesizer():
    try:
        from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer, TVAESynthesizer
        return True
    except ImportError:
        return False
