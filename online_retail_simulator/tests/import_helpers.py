def has_synthesizer():
    try:
        import online_retail_simulator.simulator_synthesizer_based
        return True
    except ImportError:
        return False
