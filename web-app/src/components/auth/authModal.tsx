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
import { api } from "~/utils/api";

const AuthModal = () => {
  const router = useRouter();
  const supabase = createClient();

  const upsertUser = api.user.upsertUser.useMutation({
    onSuccess() {

    },
    onError() {

    }
  })

  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [selected, setSelected] = useState<Key>("signin");
  const [isLoading, setIsLoading] = useState(false);

  async function logIn() {
    setIsLoading(true);
    toast.dismiss();
    toast.loading("Signing in...");

    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      console.error(error);

      toast.dismiss();
      toast.error(error.message);
    } else {
      toast.dismiss();

      await upsertUser.mutateAsync({ email });
      onOpenChange();
      router.push("/build");
    }

    setIsLoading(false);
  }

  async function signUp() {
    setIsLoading(true);
    toast.dismiss();
    toast.loading("Signing up...");

    const { error } = await supabase.auth.signUp({ email, password });
    if (error) {
      console.error(error);

      toast.dismiss();
      toast.error(error.message);
    } else {
      toast.dismiss();

      await upsertUser.mutateAsync({ email });
      onOpenChange();
      router.push("/build");
    }

    setIsLoading(false);
  }

  return (
    <>
      <Button color="primary" onPress={onOpen} isLoading={isLoading}>
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
                <p className="text-red-500">{}</p>
              </ModalBody>
              <ModalFooter>
                <Button color="danger" variant="flat" onPress={onClose}>
                  Close
                </Button>
                {
                  selected === "signin" ? (
                    <Button color="primary" onPress={logIn} isDisabled={isLoading} isLoading={isLoading}>
                      Sign in
                    </Button>
                  ) : (
                    <Button color="primary" onPress={signUp} isDisabled={isLoading} isLoading={isLoading}>
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