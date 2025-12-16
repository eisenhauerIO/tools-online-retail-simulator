def has_synthesizer():
    try:
        from sdv.single_table import CTGANSynthesizer, GaussianCopulaSynthesizer, TVAESynthesizer

        return True
    except ImportError:
        return False
