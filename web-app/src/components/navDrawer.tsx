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
      <Button onPress={onOpen} className="absolute text-2xl m-4 z-50" isIconOnly>
        =
      </Button>
      <Drawer isOpen={isOpen} onOpenChange={onOpenChange} placement="left" size="xs">
        <DrawerContent>
          {(onClose) => (
            <>
              <DrawerHeader className="flex flex-col gap-1">Navigation</DrawerHeader>
              <DrawerBody>
                <Link href="/build">
                  <Button startContent={<div className="text-2xl">⚾️</div>} className="w-full flex justify-start" size="lg">
                    Build Lineup
                  </Button>
                </Link>
                <Link href="/saved">
                  <Button startContent={<div className="text-2xl">📋</div>} className="w-full flex justify-start" size="lg">
                    Saved Lineups
                  </Button>
                </Link>
              </DrawerBody>
              <DrawerFooter>
                <Button color="danger" variant="light" onPress={signOut} className="w-full">
                  Logout
                </Button>
              </DrawerFooter>
            </>
          )}
        </DrawerContent>
      </Drawer>
    </>
  )

}

export default NavDrawer;