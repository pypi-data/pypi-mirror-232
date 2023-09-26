# Copyright (C) 2022 Bootloader.  All rights reserved.
#
# This software is the confidential and proprietary information of
# Bootloader or one of its subsidiaries.  You shall not disclose this
# confidential information and shall use it only in accordance with the
# terms of the license agreement or other applicable agreement you
# entered into with Bootloader.
#
# BOOTLOADER MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE
# SUITABILITY OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR
# A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.  BOOTLOADER SHALL NOT BE
# LIABLE FOR ANY LOSSES OR DAMAGES SUFFERED BY LICENSEE AS A RESULT OF
# USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

from majormode.perseus.model.version import Version


class AppleAppVersion:
    """
    Represent the version and the build numbers of an Apple app.  These
    strings work together to uniquely identify a particular App Store
    submission for an app.

    The version of an Apple application is defined with:

    - A version number
    - A build string

    For each new version of your app, you will provide a version number to
    differentiate it from previous versions.  The version number works
    like a name for each release of your app. For example, version `1.0.0`
    may name the first release, version `2.0.1` will name the second, and
    so on.  When submitting a new release of your app to the App Store, it
    is normal to have some false starts.  You may forget an icon in one
    build, or perhaps there is a problem in another build.  As a result,
    you may produce many builds during the process of submitting a new
    release of your app to the App Store. Because these builds will be for
    the same release of your app, they will all have the same version
    number.  But, each of these builds must have a unique build number
    associated with it so it can be differentiated from the other builds
    you have submitted for the release.  The collection of all of the
    builds submitted for a particular version is referred to as the
    'release train' for that version.


    ## Version Number

    The version number (`CFBundleShortVersionString`) is a user-visible
    string for the version of the bundle.  The required format is three
    period-separated integers, such as `10.14.1`.  The string can only
    contain numeric characters (0-9) and periods.

    Each integer provides information about the release in the format
    `[Major].[Minor].[Patch]`:

    - `Major: A major revision number.
    - `Minor`: A minor revision number.
    - `Patch`: A maintenance release number.

    This key is used throughout the system to identify the version of the
    bundle.  The version number is shown in the App Store and that
    version should match the version number you enter later in App Store
    Connect.

    ## Build String

    The build string (`CFBundleVersion`) is a machine-readable string
    composed of one to three period-separated integers, such as `10.14.1`.
    The string can only contain numeric characters (0-9) and periods.

    Each integer provides information about the release in the format
    `[Major].[Minor].[Patch]`:

    - `Major`: A major revision number.
    - `Minor`: A minor revision number.
    - `Patch`: A maintenance release number.

    You can include more integers but the system ignores them.  You can
    also abbreviate the version by using only one or two integers, where
    missing integers in the format are interpreted as zeros.  For example,
    `0` specifies `0.0.0`, `10` specifies `10.0.0`, and `10.5` specifies
    `10.5.0`.

    This key is required by the App Store and is used throughout the
    system to identify your app's released or unreleased build.  For macOS
    apps, increment the version number before you distribute a build.


    References:

    - Xcode Help; Set the version number and build string;
      https://help.apple.com/xcode/mac/current/#/devba7f53ad4

    - Technical Note TN2420; Version Numbers and Build Numbers;
      https://developer.apple.com/library/archive/technotes/tn2420/_index.html
    """

    # The key of the property list specifying the release or version number
    # of a bundle.
    PROPERTY_LIST_KEY_VERSION_NUMBER = 'CFBundleShortVersionString'

    # The key of the property list specifying the version of the build that
    # identifies an iteration of the bundle.
    PROPERTY_LIST_KEY_BUILD_NUMBER = 'CFBundleVersion'

    def __init__(
            self,
            version_number: Version,
            build_number: int or Version):
        self.__version_number = version_number
        self.__build_number = build_number

    @property
    def build_number(self) -> int or Version:
        """
        Return the build number.

        The build number is is also known as the "build string" or the
        "bundle version".


        @return: The build number.
        """
        return self.__build_number

    @property
    def version_number(self) -> Version:
        """
        Return the version number.

        The version number is also known as the marketing number.


        @return: The version number
        """
        return self.__version_number

    @property
    def plist_data(self) -> str:
        """
        Return the property list corresponding to the version and build
        numbers in respect with the plist structured text format.

        References:

        - Property List Programming Guide; Introduction to Property Lists;
          https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/PropertyLists/Introduction/Introduction.html#//apple_ref/doc/uid/10000048-CJBGDEGD

        - Information Property List Key Reference; About Information Property
          List Files;
          https://developer.apple.com/library/archive/documentation/General/Reference/InfoPlistKeyReference/Articles/AboutInformationPropertyListFiles.html


        @return: A string identifying the version and build numbers:

            ```plist
            <key>CFBundleShortVersionString</key><string>{{version_number}}</string>
            <key>CFBundleVersion</key><string>{{build_number}}</string>
            ```
        """
        return \
            f"<key>{self.PROPERTY_LIST_KEY_VERSION_NUMBER}</key><string>{self.__version_number}</string>" \
            f"<key>{self.PROPERTY_LIST_KEY_BUILD_NUMBER}</key><string>{self.__build_number}</string>"

