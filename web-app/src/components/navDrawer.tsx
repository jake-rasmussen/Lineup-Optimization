import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerBody,
  DrawerFooter,
  Button,
  useDisclosure,
} from "@heroui/react";
import Link from "next/link";
import { useRouter } from "next/router";
import toast from "react-hot-toast";
import { createClient } from "utils/supabase/component";

const NavDrawer = () => {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  const supabase = createClient();
  const router = useRouter();

  async function signOut() {
    toast.dismiss();
    toast.loading("Signing out...");

    const { error } = await supabase.auth.signOut();
    if (error) {
      console.error(error);

      toast.dismiss();
      toast.error("Error...");
    } else {
      toast.dismiss();

      onOpenChange();
      router.push("/");

      toast.dismiss();
    }
  }

  return (
    <>
      <Button onPress={onOpen} className="absolute text-2xl z-50 m-4" isIconOnly>
        =
      </Button>
      <Drawer isOpen={isOpen} onOpenChange={onOpenChange} placement="left" size="xs" className="p-0 m-0">
        <DrawerContent>
          {(onClose) => (
            <>
              <DrawerHeader className="flex flex-col gap-1"></DrawerHeader>
              <DrawerBody className="flex flex-col gap-4">
                <Link href="/build" className="flex flex-col items-center">
                  <h1 className="text-xl font-black uppercase">Lineup Optimizer</h1>
                  <img src="/Field.svg" alt="Field" style={{ width: "100%", height: "auto" }} />
                </Link>

                <div className="grow flex flex-col gap-4 justify-start my-20">
                  <Link href="/build">
                    <Button startContent={<div className="text-2xl">⚾️</div>} className="w-full flex justify-start" size="lg" variant="light">
                      Build Lineup
                    </Button>
                  </Link>
                  <Link href="/saved">
                    <Button startContent={<div className="text-2xl">📋</div>} className="w-full flex justify-start" size="lg" variant="light">
                      Saved Lineups
                    </Button>
                  </Link>
                </div>

                <Button color="danger" variant="light" onPress={signOut} className="w-full my-20">
                  Logout
                </Button>
              </DrawerBody>
            </>
          )}
        </DrawerContent>
      </Drawer>
    </>
  )

}

export default NavDrawer;