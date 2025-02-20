import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  useDisclosure,
  Input,
  Tab,
  Tabs,
} from "@heroui/react";
import { useRouter } from "next/router"
import { Key, useState } from "react"
import toast from "react-hot-toast";
import { createClient } from "utils/supabase/component";

const AuthModal = () => {
  const router = useRouter();
  const supabase = createClient();

  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [selected, setSelected] = useState<Key>("signin");
  const [loading, setLoading] = useState(false);

  async function logIn() {
    toast.dismiss();
    toast.loading("Signing in...");

    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      console.error(error);

      toast.dismiss();
      toast.error("Error...");
    } else {
      toast.dismiss();

      onOpenChange();
      router.push("/build");
    }

    setLoading(false);
  }

  async function signUp() {
    toast.dismiss();
    toast.loading("Signing up...");

    const { error } = await supabase.auth.signUp({ email, password });
    if (error) {
      console.error(error);

      toast.dismiss();
      toast.error("Error...");
    } else {
      toast.dismiss();

      onOpenChange();
      router.push("/build");
    }

    setLoading(false);
  }

  return (
    <>
      <Button color="primary" onPress={onOpen}>
        Log in
      </Button>

      <Modal isOpen={isOpen} placement="top-center" onOpenChange={onOpenChange}>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">Log in</ModalHeader>
              <ModalBody className="flex flex-col gap-4 items-center">
                <Tabs aria-label="Sign in or Sign up" selectedKey={selected as string} onSelectionChange={setSelected}>
                  <Tab key="signin" title="Sign In" />
                  <Tab key="signup" title="Sign Up" />
                </Tabs>
                <div className="flex flex-col gap-2 w-full">
                  <Input
                    label="Email"
                    placeholder="Enter your email"
                    variant="bordered"
                    value={email}
                    onValueChange={setEmail}
                  />
                  <Input
                    label="Password"
                    placeholder="Enter your password"
                    type="password"
                    variant="bordered"
                    value={password}
                    onValueChange={setPassword}
                  />
                </div>
              </ModalBody>
              <ModalFooter>
                <Button color="danger" variant="flat" onPress={onClose}>
                  Close
                </Button>
                {
                  selected === "signin" ? (
                    <Button color="primary" onPress={logIn} isDisabled={loading}>
                      Sign in
                    </Button>
                  ) : (
                    <Button color="primary" onPress={signUp} isDisabled={loading}>
                      Sign up
                    </Button>
                  )
                }

              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  )

}

export default AuthModal;