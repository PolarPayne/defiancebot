import defiance

def main():
    import sys
    if len(sys.argv) != 4:
        print("Usage: defiancebot.py <server[:port]> <channel> <nickname>")
        sys.exit(1)
    
    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        pass
        #try:
        #    port = 

if __name__ == "__main__":
    main()
