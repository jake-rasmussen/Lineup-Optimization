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
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@heroui/react";
import { useRouter } from "next/router";
import { Key, useState } from "react";
import toast from "react-hot-toast";
import { createClient } from "utils/supabase/component";
import { api } from "~/utils/api";

const AuthModal = () => {
  const router = useRouter();
  const supabase = createClient();

  const upsertUser = api.user.upsertUser.useMutation({
    onSuccess() { },
    onError() { },
  });

  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const {
    isOpen: isPopoverOpen,
    onOpen: openPopover,
    onClose: closePopover,
    onOpenChange: onPopoverChange,
  } = useDisclosure();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [forgotEmail, setForgotEmail] = useState("");

  const [selected, setSelected] = useState<Key>("signin");
  const [isLoading, setIsLoading] = useState(false);

  async function logIn() {
    setIsLoading(true);
    toast.dismiss();
    toast.loading("Signing in...");

    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
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

  async function handlePasswordReset() {
    toast.dismiss();
    toast.loading("Sending reset link...");

    const targetEmail = forgotEmail || email;
    const { error } = await supabase.auth.resetPasswordForEmail(targetEmail, {
      redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"}/reset-password`,
    });

    if (error) {
      toast.dismiss();
      toast.error(error.message);
    } else {
      toast.dismiss();
      toast.success("Reset link sent!");
      closePopover(); // manually close popover
    }
  }

  return (
    <>
      <Button color="primary" onPress={onOpen} isLoading={isLoading}>
        Get Started
      </Button>

      <Modal isOpen={isOpen} placement="top-center" onOpenChange={onOpenChange}>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">Get Started</ModalHeader>
              <ModalBody className="flex flex-col gap-4 items-center">
                <Tabs
                  aria-label="Sign in or Sign up"
                  selectedKey={selected as string}
                  onSelectionChange={setSelected}
                >
                  <Tab key="signin" title="Sign In" />
                  <Tab key="signup" title="Sign Up" />
                </Tabs>

                <div className="flex flex-col gap-2 w-full">
                  <Input
                    label="Email"
                    placeholder="Enter your email"
                    variant="bordered"
                    value={email}
                    onValueChange={(val) => {
                      setEmail(val);
                      if (!forgotEmail) setForgotEmail(val);
                    }}
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

                {selected === "signin" && (
                  <div className="w-full flex justify-start mt-1">
                    <Popover isOpen={isPopoverOpen} onOpenChange={onPopoverChange} placement="bottom-start">
                      <PopoverTrigger>
                        <button
                          className="text-sm text-blue-500 hover:underline"
                          type="button"
                          onClick={() => {
                            setForgotEmail(email);
                            openPopover();
                          }}
                        >
                          Forgot password?
                        </button>
                      </PopoverTrigger>
                      <PopoverContent className="w-72 p-4">
                        <div className="flex flex-col gap-3">
                          <p className="text-sm text-neutral-500">
                            We'll email you a link to reset your password.
                          </p>
                          <Input
                            label="Reset Email"
                            placeholder="Enter your email"
                            variant="bordered"
                            value={forgotEmail}
                            onValueChange={setForgotEmail}
                          />
                          <Button
                            size="sm"
                            color="primary"
                            onPress={handlePasswordReset}
                            isDisabled={!forgotEmail}
                          >
                            Send reset link
                          </Button>
                        </div>
                      </PopoverContent>
                    </Popover>
                  </div>
                )}
              </ModalBody>

              <ModalFooter>
                <Button color="danger" variant="flat" onPress={onClose}>
                  Close
                </Button>
                {selected === "signin" ? (
                  <Button
                    color="primary"
                    onPress={logIn}
                    isDisabled={isLoading}
                    isLoading={isLoading}
                  >
                    Sign in
                  </Button>
                ) : (
                  <Button
                    color="primary"
                    onPress={signUp}
                    isDisabled={isLoading}
                    isLoading={isLoading}
                  >
                    Sign up
                  </Button>
                )}
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
};

export default AuthModal;
