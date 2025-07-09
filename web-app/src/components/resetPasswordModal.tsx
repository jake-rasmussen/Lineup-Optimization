import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Input,
  Button,
} from "@heroui/react";
import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import toast from "react-hot-toast";
import { createClient } from "utils/supabase/component";

const ResetPasswordModal = () => {
  const supabase = createClient();
  const router = useRouter();

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionRestored, setSessionRestored] = useState(false);

  useEffect(() => {
    async function waitForSession() {
      const { data } = await supabase.auth.getSession();
      if (!data.session) {
        toast.error("Your password reset session is missing or expired.");
        return;
      }
      setSessionRestored(true);
    }

    waitForSession();
  }, []);

  async function handleResetPassword() {
    if (newPassword !== confirmPassword) {
      toast.error("Passwords do not match.");
      return;
    }

    setIsLoading(true);
    toast.dismiss();
    toast.loading("Resetting password...");

    const { error } = await supabase.auth.updateUser({ password: newPassword });

    if (error) {
      toast.dismiss();
      toast.error(error.message);
    } else {
      toast.dismiss();
      toast.success("Password reset successfully!");
      router.push("/");
    }

    setIsLoading(false);
  }

  if (!sessionRestored) return null; // Optionally render a loading spinner

  return (
    <Modal isOpen placement="top-center" hideCloseButton>
      <ModalContent>
        <>
          <ModalHeader className="flex flex-col gap-1">Reset Password</ModalHeader>
          <ModalBody className="flex flex-col gap-4 items-center">
            <div className="w-full flex flex-col gap-2">
              <Input
                label="New Password"
                placeholder="Enter your new password"
                type="password"
                variant="bordered"
                value={newPassword}
                onValueChange={setNewPassword}
              />
              <Input
                label="Confirm Password"
                placeholder="Confirm your new password"
                type="password"
                variant="bordered"
                value={confirmPassword}
                onValueChange={setConfirmPassword}
              />
            </div>
          </ModalBody>
          <ModalFooter>
            <Button
              color="primary"
              onPress={handleResetPassword}
              isLoading={isLoading}
              isDisabled={
                isLoading ||
                !newPassword ||
                !confirmPassword ||
                newPassword !== confirmPassword
              }
            >
              Reset Password
            </Button>
          </ModalFooter>
        </>
      </ModalContent>
    </Modal>
  );
};

export default ResetPasswordModal;
