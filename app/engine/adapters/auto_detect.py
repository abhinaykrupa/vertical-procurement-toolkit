"""Detect supplier from file content or filename."""


def detect(file_bytes: bytes, filename: str) -> str:
    filename_lower = filename.lower()
    if "benco" in filename_lower:
        return "Benco"
    if "henry" in filename_lower or "schein" in filename_lower or "hs_" in filename_lower:
        return "Henry Schein"
    if "base86" in filename_lower or "b86" in filename_lower:
        return "Base86"
    if "darby" in filename_lower or "drb" in filename_lower:
        return "Darby"
    if "patterson" in filename_lower or "ptn" in filename_lower:
        return "Patterson"
    if "vetcove" in filename_lower or "vc_" in filename_lower:
        return "Vetcove"
    if "ferguson" in filename_lower or "frg" in filename_lower:
        return "Ferguson"
    if "sysco" in filename_lower or "sys_" in filename_lower:
        return "Sysco"
    if "vsp" in filename_lower or "essilor" in filename_lower:
        return "VSP/Essilor"

    try:
        header = file_bytes[:2000].decode("utf-8", errors="ignore").lower()
        if "benco" in header:
            return "Benco"
        if "henry schein" in header:
            return "Henry Schein"
        if "base86" in header:
            return "Base86"
        if "darby" in header:
            return "Darby"
        if "patterson" in header:
            return "Patterson"
        if "vetcove" in header:
            return "Vetcove"
        if "ferguson" in header:
            return "Ferguson"
        if "sysco" in header:
            return "Sysco"
        if "vsp" in header or "essilor" in header:
            return "VSP/Essilor"
    except Exception:
        pass

    return "Unknown"
